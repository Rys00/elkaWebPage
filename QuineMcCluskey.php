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
    <style>
        h2 {
            margin-top: 50px;
            margin-bottom: 0;
        }
    </style>
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
        $combined = 0;
        if(isset($_POST["combined"])) {
            $combined = 1;
        }
        $finalOnly = 0;
        if(isset($_POST["finalOnly"])) {
            $finalOnly = 1;
        }
        $ones = [];
        $wildcards = [];
        for($i = 1; $i <= $n; $i++) {
            array_push($ones, $_POST["ones{$i}"]);
            array_push($wildcards, $_POST["ones{$i}"]);
        }
        $ones = join("|", $ones);
        $wildcards = join("|", $wildcards);
        $command = "python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$ones}\" --wildcards=\"{$wildcards}\" --summary={$summaryOnly} --combined={$combined} --finalOnly={$finalOnly} --html=1";
        echo shell_exec($command);
        echo "<br/><br/>Those were the results of executing command: <br/>{$command}";
    ?>
    <script>
        const links = document.querySelectorAll("a")
        links.forEach(link => {
            link.addEventListener("click", function (e) {
                e.preventDefault();
                const iframe = document.createElement("iframe");
                iframe.src = e.target.href;
                iframe.scrolling = "no";
                iframe.frameborder = "0";
                iframe.onload = function () {
                    iframe.style.height = (iframe.contentWindow.document.getElementById("karnaughMap").scrollHeight+20) + 'px';
                    iframe.style.width = (iframe.contentWindow.document.getElementById("karnaughMap").scrollWidth+20) + 'px';
                }
                e.target.parentNode.replaceChild(iframe, e.target);
                iframe.contentWindow.location.reload(true);
            });
        });

        function copy(button) {
            const copyText = document.createElement("input");
            copyText.value = button.value;
            button.appendChild(copyText);
            copyText.select();
            document.execCommand("copy");
            button.removeChild(copyText);
            button.style.setProperty("--opacity", 1);
            setTimeout(() => {
                button.style.setProperty("--opacity", 0);
            }, 2000);
        }
    </script>
</body>
</html>