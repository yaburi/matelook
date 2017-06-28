#!/usr/bin/perl

use CGI qw/:all/;

$q = new CGI;
$name = $q->param("who");

$unique = $$.time();
open (FH,">./session/$unique");
save_parameters(FH);
close (FH);

print $q -> header;

print $q -> start_html(-title => "A Sample form");
print $q -> h1("$name, please fill in this second form");

print $q -> start_form(-method => "POST",
        -action => "fo3.pl") ;

print "Your town:",$q->textfield(-name => town),$q->br;
print $q->hidden("sess",$unique);
print $q -> submit;

print $q -> end_form;

print end_html;
