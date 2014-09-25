<?php

$code = "ASD\001\002erberge";

print strlen($code)."\n";
if (strpos($code,"\001")){
	$code = str_replace(array("\001","\002","\003"), "", $code);
}
print strlen($code)."\n";