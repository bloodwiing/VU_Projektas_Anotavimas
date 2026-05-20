import argparse
import os
import math
import sys
import subprocess
import multiprocessing
import tempfile
import shutil
import heapq
import time


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Parallel wrapper for HTK's HVite command.",
        usage="%(prog)s -S SCP_FILE -i MLF_FILE [-j JOBS] [other HVite arguments...]"
    )
    
    parser.add_argument('-S', '--scp', required=True, help="Input script file (.scp) to be split.")
    parser.add_argument('-i', '--mlf', required=True, help="Output Master Label File (.mlf) to be combined.")
    parser.add_argument('-j', '--jobs', type=int, default=multiprocessing.cpu_count(),
                        help="Number of parallel HVite instances to run. Defaults to system CPU core count.")
    
    args, unknown_args = parser.parse_known_args()
    return args, unknown_args


def split_scp(scp_path, num_jobs, temp_dir):
    if not os.path.exists(scp_path):
        sys.exit(f"Error: Input SCP file '{scp_path}' not found.")

    with open(scp_path, 'r') as f:
        lines = [line.strip() for line in f if line.strip()]

    total_lines = len(lines)
    if total_lines == 0:
        sys.exit("Error: Input SCP file is empty.")

    actual_jobs = min(num_jobs, total_lines)
    
    print("[*] Profiling utterance durations to balance workload...", flush=True)
    line_weights = []
    total_weight = 0
    
    for line in lines:
        target_file = line.split()[0] 
        try:
            weight = os.path.getsize(target_file)
        except OSError:
            weight = 1
            
        line_weights.append((weight, line))
        total_weight += weight
        
    line_weights.sort(key=lambda x: x[0], reverse=True)
    
    heap = [(0, i) for i in range(actual_jobs)]
    bins = [[] for _ in range(actual_jobs)]
    weight_bins = [[] for _ in range(actual_jobs)]
    
    for weight, line in line_weights:
        current_weight, bin_idx = heapq.heappop(heap)
        
        bins[bin_idx].append(line)
        weight_bins[bin_idx].append(weight)
        
        heapq.heappush(heap, (current_weight + weight, bin_idx))

    chunk_files = []
    for i, bin_lines in enumerate(bins):
        chunk_path = os.path.join(temp_dir, f"chunk_{i}.scp")
        with open(chunk_path, 'w') as f:
            f.write("\n".join(bin_lines) + "\n")
        chunk_files.append(chunk_path)
        
    return chunk_files, actual_jobs, total_lines, weight_bins, total_weight


def merge_mlfs(mlf_files, output_mlf_path):
    with open(output_mlf_path, 'w') as out_f:
        out_f.write("#!MLF!#\n")
        
        for mlf in mlf_files:
            if not os.path.exists(mlf):
                print(f"Warning: Expected output MLF chunk '{mlf}' not found. Skipping.", file=sys.stderr)
                continue
                
            with open(mlf, 'r') as in_f:
                is_first_line = True
                for line in in_f:
                    if is_first_line and line.strip() == "#!MLF!#":
                        is_first_line = False
                        continue
                    is_first_line = False
                    out_f.write(line)


def format_size(size_bytes):
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024))) if size_bytes > 0 else 0
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_name[i]}"


def format_time(seconds):
    if math.isinf(seconds) or math.isnan(seconds):
        return "--:--:--"
    seconds = int(seconds)
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def main():
    args, unknown_args = parse_arguments()
    
    print(f"[*] Initializing Parallel HVite Wrapper...", flush=True)
    print(f"[*] Cores/Jobs requested: {args.jobs}", flush=True)
    print(f"[*] Input SCP: {args.scp}", flush=True)
    print(f"[*] Output MLF: {args.mlf}", flush=True)
    
    temp_dir = tempfile.mkdtemp(prefix="hvite_parallel_")
    processes = []
    print(f"[*] Created temporary workspace: {temp_dir}", flush=True)
    
    try:
        chunk_scps, actual_jobs, total_lines, weight_bins, total_weight = split_scp(args.scp, args.jobs, temp_dir)
        print(f"[*] Distributed {total_lines} utterances ({format_size(total_weight)}) evenly across {actual_jobs} balanced chunks.", flush=True)
        
        for i, chunk_scp in enumerate(chunk_scps):
            chunk_mlf = os.path.join(temp_dir, f"chunk_{i}.mlf")
            out_log = os.path.join(temp_dir, f"hvite_{i}.out")
            err_log = os.path.join(temp_dir, f"hvite_{i}.err")
            
            out_f = open(out_log, 'w')
            err_f = open(err_log, 'w')
            
            cmd = ["HVite", "-S", chunk_scp, "-i", chunk_mlf] + unknown_args
            p = subprocess.Popen(cmd, stdout=out_f, stderr=err_f)
            processes.append((i, p, cmd, chunk_mlf, out_f, err_f, err_log))
            
        print(f"[*] Running {actual_jobs} instances...\n", flush=True)
        
        active = True
        previous_sizes = {i: 0 for i in range(actual_jobs)}
        finished_instances = set()

        start_time = time.time()
        
        mlf_positions = {i: 0 for i in range(actual_jobs)}
        completed_count_per_job = {i: 0 for i in range(actual_jobs)}
        total_completed_weight = 0
        
        while active:
            active = False
            updates = []
            just_finished = []
            current_mlf_size = 0
            
            for i, p, cmd, chunk_mlf, out_f, err_f, err_log in processes:
                if p.poll() is None:
                    active = True
                elif i not in finished_instances:
                    finished_instances.add(i)
                    just_finished.append(str(i))
                
                try:
                    size = os.path.getsize(chunk_mlf)
                except OSError:
                    size = 0
                    
                current_mlf_size += size
                
                if size > previous_sizes[i]:
                    updates.append(str(i))
                    previous_sizes[i] = size
                
                if os.path.exists(chunk_mlf):
                    try:
                        with open(chunk_mlf, 'r') as f:
                            f.seek(mlf_positions[i])
                            for line in f:
                                # A dot on a new line signifies a completed utterance
                                if line.strip() == '.':
                                    idx = completed_count_per_job[i]
                                    if idx < len(weight_bins[i]):
                                        total_completed_weight += weight_bins[i][idx]
                                    completed_count_per_job[i] += 1
                            mlf_positions[i] = f.tell()
                    except OSError:
                        pass
                    
            if updates or just_finished:
                total_completed_count = sum(completed_count_per_job.values())
                elapsed_sec = time.time() - start_time
                
                if elapsed_sec > 0 and total_completed_weight > 0:
                    weight_per_sec = total_completed_weight / elapsed_sec
                    remaining_weight = total_weight - total_completed_weight
                    eta_sec = remaining_weight / weight_per_sec if weight_per_sec > 0 else float('inf')
                else:
                    eta_sec = float('inf')
                
                elapsed_str = format_time(elapsed_sec)
                eta_str = format_time(eta_sec)
                
                percent = (total_completed_weight / total_weight * 100) if total_weight > 0 else 0
                
                parts = []
                parts.append(f"Progress: {total_completed_count}/{total_lines} ({percent:.1f}%)")
                if updates: parts.append(f"Active I/O: {','.join(updates)}")
                if just_finished: parts.append(f"Finished: {','.join(just_finished)}")
                parts.append(f"MLF Size: {format_size(current_mlf_size)}")
                
                print(f"[ELA {elapsed_str} | ETA {eta_str}] {' | '.join(parts)}", flush=True)
                
            if active:
                time.sleep(2.0)

        print("\n[*] Processing finished. Checking for errors...", flush=True)

        has_errors = False
        for i, p, cmd, chunk_mlf, out_f, err_f, err_log in processes:
            out_f.close()
            err_f.close()
            
            if p.returncode != 0:
                has_errors = True
                print(f"\n[!] ERROR in Instance {i} (Code: {p.returncode})\nCmd: {' '.join(cmd)}", file=sys.stderr)
                try:
                    with open(err_log, 'r') as err_read:
                        print(f"STDERR:\n{err_read.read().strip()}", file=sys.stderr)
                except Exception:
                    pass
        
        if has_errors:
            sys.exit("\n[!] Aborting merge process due to errors.")
            
        merge_mlfs([p[3] for p in processes], args.mlf)
        print(f"[*] Successfully merged MLF into {args.mlf}", flush=True)

    finally:
        for proc_tuple in processes:
            if not proc_tuple[4].closed: proc_tuple[4].close()
            if not proc_tuple[5].closed: proc_tuple[5].close()
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    main()
