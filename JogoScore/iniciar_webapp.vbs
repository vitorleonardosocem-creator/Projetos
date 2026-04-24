' Arranca o JogoScore em background sem janela visível.
' Usado pelo Task Scheduler no arranque do sistema.
Dim pasta
pasta = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

Dim cmd
cmd = "cmd /c """ & pasta & "\start_JogoScore.bat"" >> """ & pasta & "\jogoscore_webapp.log"" 2>&1"

CreateObject("WScript.Shell").Run cmd, 0, False
