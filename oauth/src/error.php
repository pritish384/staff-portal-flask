<?php
session_start();

if (empty($_SESSION['errorstatus'])) {
    $error = "Something went wrong.";
} else {
    $error = $_SESSION['errorstatus'];
}

?>

<!DOCTYPE html>
<html lang="en">

<head>
	<meta charset="utf-8">
	<meta http-equiv="X-UA-Compatible" content="IE=edge">
	<meta name="viewport" content="width=device-width, initial-scale=1">

	<title>Error</title>

	<!-- Google font -->
	<link href="https://fonts.googleapis.com/css?family=Montserrat:400,700,900" rel="stylesheet">

	<!-- Custom stlylesheet -->
	<link type="text/css" rel="stylesheet" href="../dist/error.css" />

</head>

<body>

	<div id="error">
		<div class="error">
			<div class="error-404">
				<h1>Oops!</h1>
			</div>
			<p>Error:- <?php echo $error ?></p>
		</div>
	</div>

</body>

</html>