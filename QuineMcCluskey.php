<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rys00Tools</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap" rel="stylesheet">
    <style>
        :root{
            font-family: 'Roboto Mono', monospace;
        }
    </style>
</head>
<body>
    <?php
        if(!isset($_POST["submit"])){
            header("Location: index.php");
            exit();
        }
        echo shell_exec("python3 quineMcCluskey.py {$_POST["amount"]} \"{$_POST["ones"]}\"")
    ?>
</body>
</html>