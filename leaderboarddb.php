<?php
    $servername = "oceanus.cse.buffalo.edu:3306";
    $username = "jdquinn2";
    $password = "50338484";
    $db = "cse442_2023_fall_team_ai_db";
     
    // Create connection
    $conn = mysqli_connect($servername, $username, $password, $db);
     
    // Check connection
    if (!$conn) {
      die("Connection failed: " . mysqli_connect_error());
    }
    echo "Connected successfully<br>\n";

    function insertData($username, $time, $character) {
        global $conn;
        $stmt = $conn->prepare("INSERT INTO MyGuests (username, time, character) VALUES (?, ?, ?)");
        $stmt->bind_param("sss", $username, $time, $email);
        $stmt->execute();
        #$sql = "INSERT INTO Leaderboard VALUES ('$username', '$time', '$character')";
	    echo "inserted";
        if ($conn->query($sql) === TRUE) {
            return "New record created successfully";
        } else {
            return "Error: " . $sql . "<br>" . $conn->error;
        }
    }

    function retrieveData() {
        global $conn;
        $sql = "SELECT * FROM Leaderboard";
        $result = $conn->query($sql);
        $data = array();
        if ($result->num_rows > 0) {
            while ($row = $result->fetch_assoc()) {
                $data[] = $row;
            }
        }
        if (empty($data)) {
	    echo "Empty";
        }
        else {
	    foreach ($data as $value) {
	        echo "new<br>\n";
	        foreach ($value as $value2){
		    echo $value2,"<br>\n";

	        }
	        echo "<br>\n";
	    }
        }
        return $data;
    }

    if ($_SERVER["REQUEST_METHOD"] == "POST") {
        $username = $_POST["username"];
        $time = $_POST["time"];
	    $character = $_POST["character"];
        echo insertData($username, $time, $character);
    } elseif ($_SERVER["REQUEST_METHOD"] == "GET") {
        $result = retrieveData();
        echo json_encode($result);
    }
    $conn -> close();
?>