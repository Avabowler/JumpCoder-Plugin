using System;
using System.Linq;
using System.Collections.Generic;
using System.Reflection;
using System.IO;

class Program
{
    static void Main()
    {
        String[] validNames = {"System", "System.Numerics", "System.Diagnostics", "System.Collections.Generic", "System.Linq", "System.Text", "System.Security.Cryptography"};
        Assembly systemAssembly = Assembly.Load("mscorlib.dll");
        String[] fullNames = systemAssembly.GetTypes()
            .Select(t => t.FullName)
            .ToArray();
        List<string> results = new List<string>();

        foreach (String fullName in fullNames)
        {
            foreach (String validName in validNames)
            {
                if (fullName.StartsWith(validName))
                {
                    String type = fullName.Replace(validName + ".", "");
                    if (!type.Contains(".") && !type.Contains("`") && !type.Contains("+"))
                    {
                        results.Add(type);
                        break;
                    }
                }
            }
        }
        File.WriteAllText("cs_builtin.log", string.Join(",", results));
    }
}
