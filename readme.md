# AIRATS

## ACSII Image Convertor
</br>
A simple Flask web app and command-line tool to generate ASCII art from an image URL or locally.

</br>
Both Web and Command Line usage

</br>

![web](/web.jpg)



Turn any image locally or remotely into ASCII characters.

</br>


## Installation
1. Clone the repo
```bash
git clone https://github.com/bigsk1/airats.git
```
```bash
cd airats
```

2. (Optional) Create a virtual environment and activate it:

</br>

python3 -m venv venv

source venv/bin/activate

</br>

3. Install the required Python packages:

pip install -r requirements.txt

</br>

## Usage

### Web Interface

</br>

1. Run the Flask app (optional):

```bash
export FLASK_APP=app.py
```
```bash
flask run --host=0.0.0.0
```

2. Open a web browser and visit [http://localhost:5000](http://localhost:5000) to access the app.

3. Enter an image URL and width, then click "Generate ASCII Art" to see the result.

</br>


## If you don't want the virtual enviroment just make sure you have installed 
</br>

python3

python3 -m pip install Pillow

python3 -m pip install requests

run with python3 app.py in the airats folder

```bash
python3 app.py
```
Open a web browser and visit [http://localhost:5000](http://localhost:5000) to access the app.

</br>

## Command-Line Interface

</br>

Run any of the following commands:

python3 Main.py <image_url> [-w WIDTH] [-ht HEIGHT]

</br>

### Image size can be changed as needed

</br>

You can also run an image locally using

python3 Main.py your_image.jpg -w 150 -ht 50

or 

python3 Main.py https://your-image-url.jpeg -w 150 -ht 50

Into terminal

```bash
python3 Main.py rat.jpg -w 50 -ht 25
```
</br>

Output image to a file
```bash
python Main.py rat.jpg -w 80 -o output.txt
```

</br>

Supports 

    JPEG: .jpg, .jpeg
    PNG: .png
    GIF: .gif
    BMP: .bmp
    TIFF: .tif, .tiff
    ICO: .ico
    WebP: .webp

![Rat Image](/rat.jpg)

```bash
                                 
                    `,^.`:l!<;,^'   .I,           
                   !-})}rcYCQLYzvt(]?[{;          
                  "+<+}}{ruYQQQ0QJvft?--`         
                 ir1_-)jrzvucccJZwQvnj?}(,        
               .-CZJf[}rcnuzLu/tjnzvrYYcYtl       
              .1QQCL0XcnrxuO#pCjf/(|fcpXYCx,      
              ]CLXcccXJYJJXzcrttt({[{|/vLQL/^     
             +JLcrrnvYLCL0QLJCzt)]?[}}-)COLJ}`    
            !XZQcjrvXYCQQOO0QJu(}]?{?]?+zO0Lc>    
           `tL00XnjncvcczXXXvf/|{[])()[]zLCXX{    
           "rYYJYznxnvczzvuuuj({}]??][)uJCXvct'   
           ,jXXYzcvnnvzXJJJYYzvf/|fnzYCQYYzuvn^   
           .~ncccunuvcXJJXXYJ0mOqZZ00QO0JzvuvvI   
            '?xrrjrzOZJvcvXQOdkhadmQLLLLCznxczI   
              ~jrjt{)vQcvvut){(c0ZOQLLQQCcnuXX,   
   ^l>+]{){]_!,l[/)<!!]ncu1__<]tuXCLQOZQYcvXJu'   
 "+{jj|)fxuzQ0Qzxnx]!!i]cvurftuczCL0OOLJYXYJCt    
^[n/;.    .^!]rCwqQz|?{}cJLOOZZmpwmmO0QCYYCCC~    
`-/[^          '!1uQZ0CQOZmpdppkkbkpmOLCLOZOt'    
 ^_(]~!,^````^""`":~(Jdhao*#*o#MMMhZQC0mmLvj,     
   :~?}}}1)/nXzuvC0qdh#W8#abdpwmOLXXvYYvt-!I'     
      .^":;l!!l!i+-{(/tjf}???-}{1?]1(/{?<!:,'     
                              ..               
```

</br>

  ## License

This project is licensed under the MIT License.
