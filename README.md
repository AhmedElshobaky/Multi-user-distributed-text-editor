# Multi-user-distributed-text-editor-
This project is done to be submitted to CSE354 - Distributed Computing course
<p align="center">
  <img src="https://user-images.githubusercontent.com/65557776/175833564-aa63494b-5cd9-429a-84b5-aa822f4e75d6.gif">
</p>


## Files hierarchy
<p align="center">
  <img src="https://user-images.githubusercontent.com/65557776/175833773-c34e4dc7-8a96-4f98-8ec2-368efe39bedb.png">
</p>

## Links

### Link to download the installer
- https://drive.google.com/drive/folders/17k9kgl-Fn0Qs_cGyVbXJ-hTblKG4CSa_?usp=sharing

### Link to the demo video
- https://drive.google.com/drive/folders/1RmrnSsAzbynHAAU5cxST38rapaxP6RNV?usp=sharing

## How to run the application

### Run on AWS deployed server:
- Download installer.exe and run it
- Select the location of the app and Install

<p align="center">
  <img src="https://user-images.githubusercontent.com/65557776/175830105-878f8615-eeab-4c06-b9e4-b346067cd077.png">
</p>

- Once the Application installed open distributedTextEditor.exe and

<p align="center">
  <img width="600" height="500" src="https://user-images.githubusercontent.com/65557776/175831032-b629610e-187e-4da1-8e32-82354e87941d.png">
</p>

- The application should connect to the server automatically and run smoothly
<p align="center">
  <img width="600" height="500" src="https://user-images.githubusercontent.com/65557776/175831202-86c1bcf5-0f82-4a7b-8a22-ceae36cae90a.png">
</p>

- You can open any text file in the folder to edit it
<p align="center">
  <img width="600" height="500" src="https://user-images.githubusercontent.com/65557776/175831406-a3a23b26-dd22-477f-b966-dff0853d8370.png">
</p>

- You can create new file and if the name is valid the new file will be added to the server and will be editable
<p align="center">
  <img width="300" height="250" src="https://user-images.githubusercontent.com/65557776/175832369-c5334c8f-77b4-4293-aceb-3e4989b6a232.png">
</p>

- As seen the new file is added to the server and ready to be edited
<p align="center">
  <img width="600" height="500" src="https://user-images.githubusercontent.com/65557776/175832425-9e4071f6-4b08-440f-8938-b4057e7d79db.png">
</p>

### Run on Local server:
- Clone the repo or download it as zip and unzip it
- Open the Server directory, open CMD then run

```
py server.py
```

- leave it open and go back to the project directory, open CMD then run

```
py distributedTextEditor.py
```

-The application should open and be running in the local server
<p align="center">
  <img src="https://user-images.githubusercontent.com/65557776/175832911-d752cf5a-a15b-4d72-800d-dfc4701e1cdb.png">
</p>

<p align="center">
  <img width="600" height="500" src="https://user-images.githubusercontent.com/65557776/175832946-07a2606d-cab6-415b-8ac6-0cdc865d20cc.png">
</p>

### Note: Files will be stored and loaded from "/Server/documents"


