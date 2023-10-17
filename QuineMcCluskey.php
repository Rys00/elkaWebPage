<?php
    if(!isset($_POST["submit"])){
        header("Location: index.php");
        exit();
    }
    echo shell_exec("python3 quineMcCluskey.py {$_POST["amount"]} \"{$_POST["ones"]}\"")
?>