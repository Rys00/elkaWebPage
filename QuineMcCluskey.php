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
        $subsets = [];
        $subsetsId = [];
        for($i = 1; $i <= $n; $i++) {
            echo "<br/><h2>Results for function nr {$i}:</h2><br/>";
            echo shell_exec("python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$_POST["ones{$i}"]}\" --wildcards=\"{$_POST["wildcards{$i}"]}\" --summary=\"{$summaryOnly}\" --html=1");
            $subsets[$i] = [];
            array_push($subsets[1], ["/.*{$i}.*/", $_POST["ones{$i}"], $_POST["wildcards{$i}"], "{$i}"]);
        }
        if(isset($_POST["merge"])) {
            $all = array();
            for($i = 1; $i <= $n; $i++) {
                array_push($all, $i);
            }
            function createAllSubsets($set) {
                global $subsets;
                global $subsetsId;
                if(isset($subsetsId[join(";", $set)])) {
                    return;
                }
                $subsetsId[join(";", $set)] = 1;
                $n = count($set);
                $id = [];
                $nr = "";
                $onesRaw = [];
                $wildcardsRaw = [];
                for($i = $n-1; $i >= 0; $i--) {
                    if($n > 2) {
                        $newSet = $set;
                        array_splice($newSet, $i, 1); 
                        createAllSubsets($newSet);
                    }

                    if($i == $n-1) {
                        $nr = "{$set[$i]}".$nr;
                    } elseif ($i == $n-2) {
                        $nr = "{$set[$i]} and ".$nr;
                    } else {
                        $nr = "{$set[$i]}, ".$nr;
                    }
                    array_push($id, $set[$i]);
                    array_push($onesRaw, "{$_POST["ones{$set[$i]}"]}");
                    array_push($wildcardsRaw, "{$_POST["wildcards{$set[$i]}"]}");
                }
                $onesRaw = explode(";", join(";", $onesRaw));
                $wildcardsRaw = explode(";", join(";", $wildcardsRaw));
                $ones = [];
                $wildcards = [];
                $pom = [];
                for($i = 0; $i < count($onesRaw); $i++) {
                    if(!isset($pom[$onesRaw[$i]])) {
                        $pom[$onesRaw[$i]] = 0;
                    }
                    $pom[$onesRaw[$i]] += 1;
                    if($pom[$onesRaw[$i]] == $n) {
                        array_push($ones, $onesRaw[$i]);
                    }
                }
                $pom = [];
                for($i = 0; $i < count($wildcardsRaw); $i++) {
                    if(!isset($pom[$wildcardsRaw[$i]])) {
                        $pom[$wildcardsRaw[$i]] = 0;
                    }
                    $pom[$wildcardsRaw[$i]] += 1;
                    if($pom[$wildcardsRaw[$i]] == $n) {
                        array_push($wildcards, $wildcardsRaw[$i]);
                    }
                }
                $ones = explode(";", join(";", $ones));
                sort($ones);
                $ones = join(";", $ones);
                $wildcards = explode(";", join(";", $wildcards));
                sort($wildcards);
                $wildcards = join(";", $wildcards);
                array_push($subsets[$n], ["/.*".join(".*", array_reverse($id)).".*/", $ones, $wildcards, $nr]);
            }
            createAllSubsets($all);
            echo "<br/><h2>Results for merged functions nr {$subsets[$n][0][3]}:</h2><br/>";
            $result = shell_exec("python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$subsets[$n][0][1]}\" --wildcards=\"{$subsets[$n][0][2]}\" --summary=\"1\" --html=1");
            $matches = [];
            preg_match("/covers(.*)\]/", $result, $matches);
            $subsets[$n][0][4] = explode(",&nbsp", substr($matches[0], 12, -1));
            preg_match("/notation(.*)\<br/", $result, $matches);
            $subsets[$n][0][5] = substr($matches[0], 39, -10);
            echo $result;
            for ($lvl = $n-1; $lvl > 0; $lvl--) {
                for ($ssi = 0; $ssi < count($subsets[$lvl]); $ssi++) {
                    $ss = $subsets[$lvl][$ssi];
                    $toExclude = [];
                    for ($lvlhi = $lvl+1; $lvlhi <= $n; $lvlhi++) {
                        for ($psi = 0; $psi < count($subsets[$lvlhi]); $psi++) {
                            $ps = $subsets[$lvlhi][$psi];
                            if (preg_match($ss[0], $ps[0])) {
                                array_push($toExclude, $ps[1]);
                            }
                        }
                    }
                    $toExclude = explode(";", join(";", $toExclude));
                    sort($toExclude);
                    $toExclude = join(";", $toExclude);
                    if($lvl == 1) {
                        echo "<br/><h2>Results for function nr {$ss[3]} excluding all merges:</h2><br/>";
                    } else {
                        echo "<br/><h2>Results for merged functions nr {$ss[3]} excluding higher merges:</h2><br/>";
                    }
                    $result =  shell_exec("python3 quineMcCluskey.py --vars={$_POST["amount"]} --ones=\"{$ss[1]}\" --wildcards=\"{$ss[2]}\" --excluded=\"{$toExclude}\" --summary=\"1\" --html=1");
                    if (substr($result, 0 -3) != "ze!") { # minimizing not failed
                        $matches = [];
                        preg_match("/covers(.*)\]/", $result, $matches);
                        $subsets[$lvl][$ssi][4] = explode(",&nbsp", substr($matches[0], 12, -1));
                        preg_match("/notation(.*)\<br/", $result, $matches);
                        $subsets[$lvl][$ssi][5] = substr($matches[0], 39, -10);
                    }
                    echo $result;
                }
            }

            /*$lvl = 1;
            for ($ssi = 0; $ssi < count($subsets[$lvl]); $ssi++) {
                $ss = $subsets[$lvl][$ssi];
                for ($lvlhi = $n; $lvlhi > $lvl; $lvlhi--) {
                    for ($psi = 0; $psi < count($subsets[$lvlhi]); $psi++) {
                        $ps = $subsets[$lvlhi][$psi];
                        if (preg_match($ss[0], $ps[0])) {
                            $good = false;
                            for ($i = 0; $i < count($ps[4]); $i++) {
                                if (!in_array($ps[4][$i], $ss[4])) {
                                    array_push($ss[4], $ps[4][$i]);
                                    $good = true;
                                }
                            }
                            if ($good) {
                                $ss[5] = $ss[5]."&nbsp+&nbsp".$ps[5];
                            }
                        }
                    }
                }
                echo "<br/><h2>Final APN for function nr {$ssi}:</h2><br/>";
                echo "<span style='color:gold'>{$ss[5]}</span><br/>";
            }*/
        }
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
            navigator.clipboard.writeText(button.value);
            button.style.setProperty("--opacity", 1);
            setTimeout(() => {
                button.style.setProperty("--opacity", 0);
            }, 2000);
        }
    </script>
</body>
</html>