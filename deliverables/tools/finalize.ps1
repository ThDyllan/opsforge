$ErrorActionPreference = 'Stop'
$base = 'C:\Users\DyllanTHOUVIGNON\Desktop\Work\opsforge\deliverables\Dossier_de_projet_OpsForge_Dyllan_Thouvignon'
$word = New-Object -ComObject Word.Application
$word.Visible = $false; $word.DisplayAlerts = 0
$doc = $word.Documents.Open("$base.docx", $false, $false)
foreach ($i in -20, -21) {
    $st = $doc.Styles.Item([int]$i)
    $st.Font.Size = $(if ($i -eq -20) { 10.0 } else { 9.5 })
    $st.Font.Name = 'Calibri'
    $st.ParagraphFormat.SpaceAfter = $(if ($i -eq -20) { 1.5 } else { 0.5 })
    $st.ParagraphFormat.SpaceBefore = 0
    $st.ParagraphFormat.LineSpacingRule = 0
    $st.ParagraphFormat.LeftIndent = $(if ($i -eq -20) { 0 } else { 11 })
}
$doc.AutoHyphenation = $false
$doc.HyphenationZone = 20
$doc.HyphenateCaps = $false
$doc.Fields.Update() | Out-Null
$doc.TablesOfContents.Item(1).Update() | Out-Null
$doc.Repaginate()
"Sommaire : $($doc.TablesOfContents.Item(1).Range.ComputeStatistics(2)) page(s)"
"Total    : $($doc.ComputeStatistics(2)) pages, $($doc.ComputeStatistics(0)) mots"
$doc.Save()
$doc.ExportAsFixedFormat("$base.pdf", 17, $false, 0, 0, 0, 0, 0, $true, $true, 0, $true, $true, $false)
$doc.Close(0); $word.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($word) | Out-Null

