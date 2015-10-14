# Tower for Desktop

Browser-based GCS that runs on Desktop via Electron.

![https://cloud.githubusercontent.com/assets/12703357/10495186/94ea2e34-7288-11e5-8a03-099565d5dfce.png](https://cloud.githubusercontent.com/assets/12703357/10495186/94ea2e34-7288-11e5-8a03-099565d5dfce.png)


## Running

```
sudo -H pip install -UI git+https://github.com/3drobotics/tower-desktop.git
tower tcp:127.0.0.1:5760
```

Then open <http://localhost:24403/> in a browser.


## Running in a Electron window

```
git clone https://github.com/3drobotics/tower-desktop.git
cd tower-desktop
pip install -r requirements.txt
npm install -g electron-shell
electron . tcp:127.0.0.1:5760
```


## License

MIT/Apache-2.0
