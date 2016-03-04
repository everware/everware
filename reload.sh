PID=`pgrep jupyterhub`
[ -z "$PID" ] && echo "Cannot find jupyterhub running" && exit 1
pkill -1 jupyterhub 
echo "Reloaded"
