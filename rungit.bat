
@REM echo "GIT checkout at dev"
git checkout dev

@REM echo "GIT pull"
git pull

@REM echo "Enter the message for git commit : "

set /p cm=Please put the message :  



git add .

git commit -m %cm%

git push origin dev