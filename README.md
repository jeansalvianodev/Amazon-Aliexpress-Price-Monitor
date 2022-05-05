<h1 align="center">
<br>
  <img src="https://i.imgur.com/hdUNdF7.png" alt="Price Monitoring Bot" width="300">
<br>
<br>
<b>Price Monitoring Bot</b>
</h1>

<p align="center"><b>Amazon and Aliexpress store price monitoring bot (PT-BR).</b></p>



[//]: # (Add your gifs/images here:)
<div align="center">

  <img src="https://i.imgur.com/kxNuB7C.gif" alt="demo" height="480">
  
</div>

<hr />

## <b>What does it do?</b> 
The Price Monitor Bot, as its name implies, monitors the price of a desired product, so that when the price of this product reaches the value specified by the user, the user is notified via email.

## <b>Getting started</b>

### <b>First of all you must configure the account that will send the emails.</b>

Needs to be a Gmail account!
<div>
  <img src="https://i.imgur.com/6XFIEhI.png" alt="config" height="220">
</div>
When filling in the data, it is not necessary to use quotation marks (")

### - <b>Now you need to install some libraries</b>


- **PySimpleGUI** — A Python package that enables Python programmers of all levels to create GUIs.
- **playwright** — A Python library to automate Chromium, Firefox and WebKit browsers with a single API.
- **validators** — Python Data Validation for Humans.


``` 
pip install PySimpleGUI
pip install playwright
pip install validators
```
### <b>Notes</b>: 
- The software only works on Brazilian websites.
- If the link is not a product in the store, there will be no answers!
- The email will only be sent when the price you chose is greater than or equal to the price of the product.
- If the entered value is less than the product's price, the software will save the data (product link, user email and the chosen value), so when the program is reopened, it will not be necessary to fill in the data.
- If you want to choose another product, there is the "Resetar" option, which will erase the data.
