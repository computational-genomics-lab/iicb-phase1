#!/bin/bash  
#read -p "ENTER IP ADDRESS:" NEW_IP
#read -p "ENTER PORT:" PORT
#unset CONFIG_FILE

#CONFIG_FILE=$(find / -name configuration.ini -print -quit)
CONFIG_FILE='configuration.ini'
#source <(grep CONFIG_FILE $CONFIG_FILE)
CONFIG_FILE=$CONFIG_FILE

source <(grep ENV_FILE_PATH $CONFIG_FILE)
ENV_FILE_PATH=$ENV_FILE_PATH

source <(grep FRONTEND_FOLDER_PATH $CONFIG_FILE)
FRONTEND_FOLDER_PATH=$FRONTEND_FOLDER_PATH

source <(grep BACKEND_FOLDER_PATH $CONFIG_FILE)
BACKEND_FOLDER_PATH=$BACKEND_FOLDER_PATH


source <(grep IP_ADDRESS $CONFIG_FILE)
NEW_IP=$IP_ADDRESS

source <(grep FRONTEND_PORT $CONFIG_FILE)
FRONTEND_PORT=$FRONTEND_PORT

source <(grep BACKEND_PORT $CONFIG_FILE)
BACKEND_PORT=$BACKEND_PORT

source <(grep APACHE_PORT $CONFIG_FILE)
APACHE_PORT=$APACHE_PORT


kill -9 $(lsof -t -i:$FRONTEND_PORT)
kill -9 $(lsof -t -i:$BACKEND_PORT) &



#PORT=8000 
#NEW_IP=192.168.1.11
source $ENV_FILE_PATH/bin/activate 
python $BACKEND_FOLDER_PATH/manage.py runserver $NEW_IP:$BACKEND_PORT &
sleep 4&

#echo "FRONT END STARTED"&
wait  4&
#cd /home/azure/Downloads/Angular_Js-17Oct 
#cd /home/sutripa/Azure_IICB_FrontEnd_Unzip/eumicrobedb-master-30-10-19

cd $FRONTEND_FOLDER_PATH

sed -i -r 's/"aboutUs": ?.*/"aboutUs": "http:\/\/IP:PORT\/media\/ABOUT_US\/",/g' $FRONTEND_FOLDER_PATH/src/assets/config.json
sed -i -r "s/IP/$NEW_IP/g" $FRONTEND_FOLDER_PATH/src/assets/config.json
sed -i -r "s/PORT/$APACHE_PORT/g" $FRONTEND_FOLDER_PATH/src/assets/config.json

sed -i -r 's/"browserDetailsMediaUrl" ?.*/"browserDetailsMediaUrl": "http:\/\/IP:PORT\/media\/SCI_OUT\/",/g' $FRONTEND_FOLDER_PATH/src/assets/config.json
sed -i -r "s/IP/$NEW_IP/g" $FRONTEND_FOLDER_PATH/src/assets/config.json
sed -i -r "s/PORT/$APACHE_PORT/g" $FRONTEND_FOLDER_PATH/src/assets/config.json

sed -i -r 's/"dndMediaUrl" ?.*/"dndMediaUrl": "http:\/\/IP:PORT\/media\/dnd\/"/g' $FRONTEND_FOLDER_PATH/src/assets/config.json
sed -i -r "s/IP/$NEW_IP/g" $FRONTEND_FOLDER_PATH/src/assets/config.json
sed -i -r "s/PORT/$APACHE_PORT/g" $FRONTEND_FOLDER_PATH/src/assets/config.json

#sed -i -r "s/PORT/$APACHE_PORT/g" config.json


#sed -i -r"s/localhost/$NEW_IP/g" \
#       -r sed -i -r "s/(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])/$NEW_IP/g" /home/sutripa/Azure_IICB_FrontEnd_Unzip/eumicrobedb-master-30-10-19/src/assets/config.json

#sed -i -r "s/:[0-9]+/:$BACKEND_PORT/g" $FRONTEND_FOLDER_PATH/src/assets/config.json


sed -i -r "s/:[0-9]+/:$BACKEND_PORT/g"  $FRONTEND_FOLDER_PATH/proxy.conf.json


sed -i -r "s/(([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){3}([0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])/$NEW_IP/g" $FRONTEND_FOLDER_PATH/proxy.conf.json
sudo npm install
sudo npm update
ng serve --proxy-config proxy.conf.json --host $NEW_IP --port $FRONTEND_PORT  --disableHostCheck



wait
echo "IICB RUNNING ...."

