<?php
include './db/db.php';
if(!$_SESSION['logged_in']){
  header('Location: oauth/src/index.php');
  exit();
}
extract($_SESSION['userData']);

$config = json_decode(file_get_contents('./oauth/config.json'), true);

$sql = "SELECT * FROM members WHERE discord_id = '$discord_id'";
$result = $conn->query($sql);

// if $discord_id is in the database, then redirect to the dashboard
if ($result->num_rows > 0) {
  $staff_data = $result->fetch_assoc();
  $staff_code = $staff_data['staff_code'];
  $staff_role = $staff_data['role'];
  $staff_salary = $staff_data['salary'];
}else{
  $_SESSION['errorstatus'] = "You are not a staff member!";
  header('Location: oauth/src/error.php');
  exit();
  
}





?>