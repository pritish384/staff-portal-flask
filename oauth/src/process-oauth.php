<?php
$config = json_decode(file_get_contents('../config.json'), true);

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

if(!isset($_GET['code'])){
    echo 'no code';
    exit();
}

$discord_code = $_GET['code'];
$bot_token = $config['bot_token'];


$payload = [
    'code'=>$discord_code,
    'client_id'=>$config['client_id'],
    'client_secret'=>$config['client_secret'],
    'grant_type'=>$config['grant_type'],
    'redirect_uri'=>$config['redirect_uri'],
    'scope'=>$config['scope']
];



$payload_string = http_build_query($payload);
$discord_token_url = "https://discordapp.com/api/oauth2/token";

$ch = curl_init();

curl_setopt($ch, CURLOPT_URL, $discord_token_url);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload_string);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);

$result = curl_exec($ch);

if(!$result){
    echo curl_error($ch);
}

$result = json_decode($result,true);
$access_token = $result['access_token'];

$discord_users_url = "https://discordapp.com/api/users/@me";
$discord_guilds_url = "https://discordapp.com/api/users/@me/guilds";
$header = array("Authorization: Bearer $access_token", "Content-Type: application/x-www-form-urlencoded");

$ch = curl_init();
curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
curl_setopt($ch, CURLOPT_URL, $discord_users_url);
curl_setopt($ch, CURLOPT_POST, false);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);

$result = curl_exec($ch);
$result = json_decode($result, true);




session_start();

$_SESSION['logged_in'] = true;
$_SESSION['userData'] = [
    'name'=>$result['username'],
    'discord_id'=>$result['id'],
    'avatar_url'=>"https://cdn.discordapp.com/avatars/".$result['id']."/".$result['avatar'].".jpg",
    'discriminator'=>$result['discriminator'],
    'guilds'=>getUsersGuilds($access_token),
    'member_roles'=>getGuildMemberRoles($config['guild_id'], $result['id'], $bot_token)
];



header('Location: ../../index.php');
exit();


function getUsersGuilds($auth_token){
    //url scheme /users/@me/guilds
    $discord_api_url = "https://discordapp.com/api";
    $header = array("Authorization: Bearer $auth_token","Content-Type: application/x-www-form-urlencoded");
    $ch = curl_init();
    //set the url, number of POST vars, POST data
    curl_setopt($ch, CURLOPT_HTTPHEADER,$header);
    curl_setopt($ch,CURLOPT_URL, $discord_api_url.'/users/@me/guilds');
    curl_setopt($ch,CURLOPT_POST, false);
    //curl_setopt($ch,CURLOPT_POSTFIELDS, $fields_string);
    curl_setopt($ch,CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
    $result = curl_exec($ch);
    $result = json_decode($result,true);
    return $result;
}


function getGuildMemberRoles($guild_id, $user_id , $bot_token) {
    $discord_api_url = "https://discordapp.com/api";
    $header = array("Authorization: Bot $bot_token", "Content-Type: application/x-www-form-urlencoded");
    $ch = curl_init();
    curl_setopt($ch, CURLOPT_HTTPHEADER, $header);
    curl_setopt($ch, CURLOPT_URL, $discord_api_url."/guilds/$guild_id/members/$user_id");
    curl_setopt($ch, CURLOPT_POST, false);
    curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
    curl_setopt($ch, CURLOPT_SSL_VERIFYHOST, 0);
    curl_setopt($ch, CURLOPT_SSL_VERIFYPEER, 0);
    $result = curl_exec($ch);
    $response_code = curl_getinfo($ch, CURLINFO_RESPONSE_CODE);
    if ($response_code != 200) {
        throw new Exception("Failed to get member roles: " . $result);
    }
    $result = json_decode($result, true);
    return $result['roles'];
}


?>