<?php
$config = json_decode(file_get_contents('../config.json'), true);
$discord_url = $config['auth_url'];


header("Location: $discord_url");
exit();

?>