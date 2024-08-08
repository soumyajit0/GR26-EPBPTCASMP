There is two part:- 1) API Server Part & 2) Firefox Add-on/ Extension Part

1) In API Server, We have to install some dependency
```
pip install fastapi uvicorn
```
Then go to the API folder and then run 
```
python api.py

or

python3 api.py

```
2) In extension/add-on part

1. click on Extensions
2. click on manage extensions
3. click on manage your extensions cog wheel
4. click on Debug add ons
5. click on Load temporary add on
7. select the File `manifest.json` under `FB_scrapping/extension` subfolder
8. click on open, Now go to facebook and go to someone's profile
    You should see the post text's on your terminal

Please go to ```about:debugging``` then click on “This Firefox” Then Load temporary Extension and Please select the ```Manifest.JSON``` file. 

Then we are good to go with the extention

