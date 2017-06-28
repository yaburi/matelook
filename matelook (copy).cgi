#!/usr/bin/perl -w
# By Nathan Zhen [z5017458], Oct 2016

use CGI qw/:all/;
use CGI::Carp qw/fatalsToBrowser warningsToBrowser/;

use File::Basename;


sub main() {
    # print start of HTML ASAP to assist debugging if there is an error in the script
    print page_header();
    
    # Now tell CGI::Carp to embed any warning in HTML
    warningsToBrowser(1);
    
    # define some global variables
    $debug = 1;
    $users_dir = "dataset-medium";
    
    $cgi = CGI->new();
    $param = $cgi->param('param');
    #print "$param\n";
    
    print user_page();
    print page_trailer();
}


#
# Show unformatted details for user "n".
# Increment parameter n and store it as a hidden variable
#
sub user_page {
    my $n = param('n') || 0;
    #my @users = sort(glob("$users_dir/*"));
    if (!defined $param) {
        $user_to_show  = "$users_dir/z3275760";
    } else {
        $user_to_show = "$users_dir/$param";
        #print "GGG\n";
    }
    my $details_filename = "$user_to_show/user.txt";
    open my $p, "$details_filename" or die "can not open $details_filename: $!";
    $details = join '', <$p>;
    
    # We format the details to something readable
    $details = format_details($details);
    
    close $p;
    
    # Profile picture directory
    my $prof_pic_filename = "$user_to_show/profile.jpg";
    # The list of user posts on their page (sorted in reverse chronological order)
    my @posts_list = generate_user_posts();
    # The next user parameter
    my $next_user = $n + 1;
    
    # Below object tags were taken from: 
    # http://stackoverflow.com/questions/22051573/how-to-hide-image-broken-icon-using-only-css-html-without-js
    # Gives a default image if there isn't a profile picture defined
    return <<eof
<form method="POST" action="">
    <input type="hidden" name="n" value="$next_user">
    <input type="submit" value="Next user" class="matelook_button">
</form>
<div class="matelook_user_details">
<object class="avatar" data="$prof_pic_filename" type="image/jpg"><img src="default.gif"/></object>
$details
</div>
<p>
<div class="matelook_user_posts_bg">
@posts_list
</div>
eof
}


#
# HTML placed at the top of every page
#
sub page_header {
    return <<eof
Content-Type: text/html

<!DOCTYPE html>
<html lang="en">
<head>
<title>matelook</title>
<link href="matelook.css" rel="stylesheet">
</head>
<body>
<div class="matelook_heading">
<a href="./matelook.cgi">
matelook
</a>
</div>
eof
}



sub format_details {
    my ($details) = @_;
    my @details_arr = ();
    
    # ===== PUBLIC INFORMATION ===== #
    if ($details =~ /full\_name\=(.*)\s*/) {
        my $full_name = "<h2>$1</h2>";
        push @details_arr, $full_name;
    }
    if ($details =~ /zid\=(.*)\s*/) {
        my $zid = "zID: $1\n";
        push @details_arr, $zid;
    }
    if ($details =~ /program\=(.*)\s*/) {
        my $program = "Program: $1\n";
        push @details_arr, $program;
    }
    if ($details =~ /birthday\=(.*)\s*/) {
        my $birthday = "Birthday: $1\n";
        push @details_arr, $birthday;
    }
    if ($details =~ /home\_suburb\=(.*)\s*/) {
        my $home_suburb = "From: $1\n";
        push @details_arr, $home_suburb;
    }
    if ($details =~ /mates\=(.*)\s*/) {
#        my $mates = "Mates with: $1\n";
#        push @details_arr, $mates;
        my $mates = $1;
        my @mates_arr = split /,/, $mates;
        push @details_arr, "<b>Mates with:</b>";
        foreach my $zid (@mates_arr) {
            $zid =~ s/(\[|\]|\,|\s+)//g;
            open my $file, "$users_dir/$zid/user.txt" or die "can not open $details_filename: $!";
            my $name = join '', <$file>;
            $name =~ /full\_name\=(.*)\s*/;
            $name = $1;
            $mate_profile = "<div class=\"mates_list\"><div class=\"user_thumbnail\"><a href=\"./matelook.cgi?param=$zid\"><object class=\"avatar\" data=\"$users_dir/$zid/profile.jpg\" type=\"image/jpg\"><img src=\"default.gif\"/></object></a></div><a href=\"./matelook.cgi?param=$zid\">$name</a></div>\n";
            push @details_arr, $mate_profile;
        }
#        push @details_arr, "</div>";
        
    }
    
    # ===== PRIVATE INFORMATION ===== #
    if ($details =~ /email\=(.*)\s*/) {
        my $email = "Email: $1\n";
        push @details_arr, $email;
    }
    if ($details =~ /password\=(.*)\s*/) {
        my $password = "Password: $1\n";
        push @details_arr, $password;
    }
    if ($details =~ /courses\=(.*)\s*/) {
        my $courses = "Courses: $1\n";
        $courses =~ s/[\[|\]]//g;
        my @courses_arr = split /,/, $courses;
        foreach my $course (@courses_arr) {
            $course =~ s/^\s+|\s+$//;
            $course = "$course, ";
        }
        $courses = join '', @courses_arr;
        $courses =~ s/,\s+$//;
        push @details_arr, $courses;
    }
    if ($details =~ /home\_longitude\=(.*)\s*/) {
        my $home_longitude = "Home longitude: $1\n";
        push @details_arr, $home_longitude;
    }
    if ($details =~ /home\_latitude\=(.*)\s*/) {
        my $home_latitude = "Home latitude: $1\n";
        push @details_arr, $home_latitude;
    }
    
    $f_details = join '', @details_arr;
    return $f_details;
}

sub generate_user_posts {
    #my $n = param('n') || 0;
    #my @users = sort(glob("$users_dir/*"));
    if (!defined $param) {
        $user_to_show  = "$users_dir/z3275760";
    } else {
        $user_to_show = "$users_dir/$param";
    }

    # Iterates through the posts
    # Taken from Wk11 Tutorial given code
    my %post_hash = ();
    my $folder_num = 0;
    my @posts_arr = ();
    #foreach my $post_filename (sort(glob"$user_to_show/posts/*/post.txt")) {
    foreach my $post_filename (glob("$user_to_show/posts/*/post.txt")) {
        #print "$post_filename<br>";
        $post_filename =~ /posts\/(.*)\/post\.txt/;
        $folder_num = $1;
        #print "$folder_num<br>";
        open my $f, "$post_filename" or die "can not open $post_filename: $!";
        $file_time = join '', <$f>;
        $file_time =~ /time\=(.*)\s*/;
        $file_time = $1;
        $post_hash{$file_time} = $folder_num;
        #$folder_num++;
        close $f;
    }
    foreach $file_time (reverse sort keys %post_hash) {
        #printf "%-8s %s<br>\n", $file_time, $post_hash{$file_time};
        open $posts_file, "$user_to_show/posts/$post_hash{$file_time}/post.txt" or die "can not open $user_to_show/posts/$post_hash{$file_time}/post.txt: $!";
        $posts_file_contents = join ' ', <$posts_file>;
        $posts_file_contents =~ s/\n/\<br\>\n/g;
        $posts_file_contents .= "<br>\n";
        push @posts_arr, $posts_file_contents;
    }
    
    #my $posts_list = join '', @posts_arr;
    close $posts_file;
    #my $posts_list = format_user_post(@posts_arr);
    #return $posts_list;
    my @formatted_posts = format_user_post(@posts_arr);
    return @formatted_posts;

}

# Formats the user posts to a consistent form.
sub format_user_post {

    # The array of posts before formatting
    my (@old_posts_arr) = @_;
    # The array of posts after formatting
    my $posts_arr = ();
    
    
    # Goes through each post and formats it
    foreach my $posts (@old_posts_arr) {
        # Separates each post with div
        push @posts_arr, "\<div class\=\"matelook_user_posts\"\>\n";
        
        # Regex to format post
        if ($posts =~ /from\=(.*)\s*/) {
            my $from = "From: $1\n";
            push @posts_arr, $from;
        }
        if ($posts =~ /time\=(.*)\s*/) {
            my $time = "Time: $1\n";
            push @posts_arr, $time;
        }
        if ($posts =~ /message\=(.*)\s*/) {
            my $message = "<p>$1\n</p>";
            $message =~ s/\\n/<br>/g;
            push @posts_arr, $message;
        }
        if ($posts =~ /longitude\=(.*)\s*/) {
            my $longitude = "Longitude: $1\n";
            push @posts_arr, $longitude;
        }
        if ($posts =~ /latitude\=(.*)\s*/) {
            my $latitude = "Latitude: $1\n";
            push @posts_arr, $latitude;
        }
        
        # Adds a break between each post (with each post separated by div)
        push @posts_arr, "</div>";
    }
    return @posts_arr;
}

#
# HTML placed at the bottom of every page
# It includes all supplied parameter values as a HTML comment
# if global variable $debug is set
#
sub page_trailer {
    my $html = "";
    $html .= join("", map("<!-- $_=".param($_)." -->\n", param())) if $debug;
    $html .= end_html;
    return $html;
}


main();
