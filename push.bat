git pull
set /p var=����������:
git add -A
git commit -m "%var% %date:~0,10%"
git push origin master
