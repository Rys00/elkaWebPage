<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rys00Tools</title>
    <link rel="stylesheet" href="main.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Lobster&family=Solitreo&display=swap" rel="stylesheet">
</head>
<body>
    <?php
        if(!isset($_POST["submit"])){
            header("Location: index.php");
            exit();
        }
        $n = $_POST["quineFunctionAmount"];
        $summaryOnly = 0;
        if(isset($_POST["summaryOnly"])) {
            $summaryOnly = 1;
        }
        for($i = 1; $i <= $n; $i++) {
            echo "Results for function nr {$i}:<br/>";
            echo shell_exec("python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$_POST["ones{$i}"]}\" --wildcards=\"{$_POST["wildcards{$i}"]}\" --summary=\"{$summaryOnly}\" --html=1");
        }
    ?>
</body>
</html>