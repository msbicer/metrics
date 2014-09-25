<?php

require 'PHP-Parser-1.0.0beta1/lib/bootstrap.php';

ini_set('xdebug.max_nesting_level', 2000);
ini_set("memory_limit","1024M");

// $code = "<?php echo 'Hi ', hi\\getTarget();";

// $parser = new PhpParser\Parser(new PhpParser\Lexer);

// try {
//     $stmts = $parser->parse($code);
// } catch (PhpParser\Error $e) {
//     echo 'Parse Error: ', $e->getMessage();
// }

// print_r($stmts);

//const IN_DIR  = '/Users/sbicer/Desktop/akademik/phpmyadmin/phpmyadmin-git/';
//const OUT_DIR = '/Users/sbicer/Desktop/akademik/parser/phpmyadmin/';

// $IN_DIR  = '/Users/sbicer/Desktop/akademik/parser/test/';
// $OUT_DIR = '/Users/sbicer/Desktop/akademik/parser/';

if ($argc != 3){
    echo "php parse.php in_dir out_dir";
    return;
}

$IN_DIR  = $argv[1];
$OUT_DIR  = $argv[2];

mkdir($OUT_DIR);

// use the emulative lexer here, as we are running PHP 5.2 but want to parse PHP 5.3
$parser        = new PhpParser\Parser(new PhpParser\Lexer\Emulative);
$traverser     = new PhpParser\NodeTraverser;
$prettyPrinter = new PhpParser\PrettyPrinter\Standard;

$traverser->addVisitor(new PhpParser\NodeVisitor\NameResolver); // we will need resolved names
//$traverser->addVisitor(new NodeVisitor\NamespaceConverter);     // our own node visitor

// iterate over all .php files in the directory
$files = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($IN_DIR));
$files = new RegexIterator($files, '/php$/');

$serializer = new PhpParser\Serializer\XML;

foreach ($files as $file) {
    try {

        // read the file that should be converted
        $code = file_get_contents($file);
        
        // if (!strpos($file->getPathname(), "cookie")){
        //     continue;
        // }

        $code = str_replace(array("\\0","\\x"), "", $code);

        // parse
        $stmts = $parser->parse($code);

        // traverse
        $stmts = $traverser->traverse($stmts);

        // pretty print
        $code = '<?php ' . $prettyPrinter->prettyPrint($stmts);

        // write the converted file to the target directory
        // echo $file->getPathname()." ".OUT_DIR;
        $path =  substr_replace($file->getPathname(), $OUT_DIR, 0, strlen($IN_DIR));
        echo $path." ".memory_get_usage()." ".ini_get("memory_limit")."\n";

        $dir = substr($path, 0, strrpos($path, '/'));
        if (!file_exists($dir))
            mkdir($dir, 0777, true);

        file_put_contents(
            $path,
            // $code
            $serializer->serialize($stmts)
        );
    } catch (Exception $e) {
        echo 'Parse Error: ', $e->getMessage();
    }
}

echo "REGULAR_EXIT\n";