using System;
using System.IO;
using System.Runtime.InteropServices;
using System.Text;

internal class Program
{
    [DllImport("transcrLUSS.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int initTranscrLUSS(byte[] katVardas);

    [DllImport("transcrLUSS.dll", CallingConvention = CallingConvention.Cdecl)]
    private static extern int KircTranskr(
        byte[] sak,
        byte[] TrSak,
        int TrSakIlg,
        ushort[] unitsR,
        ushort[] unitsRNextSep,
        int[] unitsLet,
        int[] letPos,
        int rules2use
    );

    private static int Main(string[] args)
    {
        if (args.Length != 3)
        {
            Console.Error.WriteLine("Naudojimas:");
            Console.Error.WriteLine("  transcrLUSS.exe <rules_dir> <input.txt> <output.txt>");
            Console.Error.WriteLine();
            Console.Error.WriteLine("Pavyzdys:");
            Console.Error.WriteLine(@"  transcrLUSS.exe C:\rules in.txt out.txt");
            return 2;
        }

        string rulesDir = args[0];
        string inputPath = args[1];
        string outputPath = args[2];

        Encoding.RegisterProvider(CodePagesEncodingProvider.Instance);
        Encoding cp1257 = Encoding.GetEncoding(1257);

        if (!Directory.Exists(rulesDir))
        {
            Console.Error.WriteLine($"Klaida: katalogas nerastas: {rulesDir}");
            return 2;
        }

        if (!File.Exists(inputPath))
        {
            Console.Error.WriteLine($"Klaida: įvesties failas nerastas: {inputPath}");
            return 2;
        }

        byte[] rulesDirBytes = Encoding.ASCII.GetBytes(rulesDir + "\0");
        int rc = initTranscrLUSS(rulesDirBytes);
        if (rc != 0)
        {
            Console.Error.WriteLine($"initTranscrLUSS klaida: {rc}");
            return 1;
        }

        string[] lines;
        try
        {
            lines = ReadAllLinesSmart(inputPath, cp1257);
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Klaida skaitant įvesties failą: {ex.Message}");
            return 1;
        }

        try
        {
            var writer = new StreamWriter(outputPath, false, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false));

            const int TR_BUF = 65536;
            const int MAX_PHON = 20000;

            byte[] trBuf = new byte[TR_BUF];
            ushort[] unitsR = new ushort[MAX_PHON];
            ushort[] unitsSep = new ushort[MAX_PHON];
            int[] unitsLet = new int[MAX_PHON];

            foreach (var rawLine in lines)
            {
                string line = rawLine?.Trim();
                if (string.IsNullOrEmpty(line))
                {
                    writer.WriteLine();
                    continue;
                }

                byte[] sak = cp1257.GetBytes(line.ToUpper() + "\0");

                int[] letPos = new int[line.Length + 1];
                for (int i = 0; i < letPos.Length; i++) letPos[i] = i;

                Array.Clear(trBuf, 0, trBuf.Length);
                Array.Clear(unitsR, 0, unitsR.Length);
                Array.Clear(unitsSep, 0, unitsSep.Length);
                Array.Clear(unitsLet, 0, unitsLet.Length);

                int phonCount = KircTranskr(
                    sak,
                    trBuf,
                    trBuf.Length,
                    unitsR,
                    unitsSep,
                    unitsLet,
                    letPos,
                    75
                );

                string trText = BytesToNullTerminatedString(trBuf, cp1257);

                writer.WriteLine(trText);
            }

            writer.Close();
        }
        catch (Exception ex)
        {
            Console.Error.WriteLine($"Klaida rašant išvesties failą: {ex.Message}");
            return 1;
        }

        Console.WriteLine("OK");
        return 0;
    }

    private static string[] ReadAllLinesSmart(string path, Encoding cp1257)
    {
        try
        {
            return File.ReadAllLines(path, new UTF8Encoding(encoderShouldEmitUTF8Identifier: false, throwOnInvalidBytes: true));
        }
        catch
        {
            return File.ReadAllLines(path, cp1257);
        }
    }

    private static string BytesToNullTerminatedString(byte[] buffer, Encoding enc)
    {
        int len = Array.IndexOf(buffer, (byte)0);
        if (len < 0) len = buffer.Length;
        return enc.GetString(buffer, 0, len);
    }
}
