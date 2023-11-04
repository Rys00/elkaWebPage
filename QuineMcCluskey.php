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
            echo "<br/><h2>Results for function nr {$i}:</h2><br/>";
            echo shell_exec("python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$_POST["ones{$i}"]}\" --wildcards=\"{$_POST["wildcards{$i}"]}\" --summary=\"{$summaryOnly}\" --html=1");
        }
        if(isset($_POST["merge"])) {
            $all = array();
            for($i = 1; $i <= $n; $i++) {
                array_push($all, $i);
            }
            function executeForSet($set) {
                $n = count($set);
                $nr = "";
                $ones = "";
                $wildcards = "";
                for($i = $n-1; $i >= 0; $i--) {
                    if($n > 2) {
                        $newSet = $set;
                        array_splice($newSet, $i, 1); 
                        executeForSet($newSet);
                    }

                    if($i == $n-1) {
                        $nr = "{$set[$i]}".$nr;
                    } elseif ($i == $n-2) {
                        $nr = "{$set[$i]} and ".$nr;
                    } else {
                        $nr = "{$set[$i]}, ".$nr;
                    }
                    $ones = "{$_POST["ones{$set[$i]}"]};".$ones;
                    $wildcards = "{$_POST["wildcards{$set[$i]}"]};".$wildcards;
                }
                echo "<br/><h2>Results for merged functions nr {$nr}:</h2><br/>";
                echo shell_exec("python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$ones}\" --wildcards=\"{$wildcards}\" --summary=\"1\" --mergeLevel={$n} --html=1");
            }
        }
        executeForSet($all);
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
            });
        });
    </script>
</body>
</html>