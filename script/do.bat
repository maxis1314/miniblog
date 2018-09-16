
:start
echo new batch %date% %time%

python 0.extrac.py
python 1.fenci.py
python 2.merge.py
python 4.cluster.py
python 6.tuijian.py

timeout 600 > NUL
goto start

pause