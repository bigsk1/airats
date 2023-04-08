# AIRATS  

## ASCII Image Convertor 
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
</br>
A simple Flask web app and command-line tool to generate ASCII art from an image URL or locally.

</br>
Both Web and Command Line usage

</br>
</br>

![fish](/images/fish.jpg)



Turn any image locally or remotely into ASCII characters.

</br>


# Installation

## Linux

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)


1. Clone the repo
```bash
git clone https://github.com/bigsk1/airats.git
```
```bash
cd airats
```

2. (Optional) Create a virtual environment and activate it:

```bash
python3 -m venv venv

source venv/bin/activate
```
</br>

3. Install the required Python packages:

```bash
pip install -r requirements.txt
```
</br>
</br>

## Ubuntu 22.04+
![Ubuntu](https://img.shields.io/badge/Ubuntu-E95420?style=for-the-badge&logo=ubuntu&logoColor=white)
### If you don't want the virtual enviroment just make sure you have installed 
</br>

```bash
sudo apt install python3 && sudo apt install python3-pip && sudo apt install python3-flask && python3 -m pip install Pillow && python3 -m pip install requests
```
run with python3 app.py in the airats folder

```bash
python3 app.py
```
Open a web browser and visit [http://localhost:5000](http://localhost:5000) to access the app.

</br>
</br>

## Windows 64bit install
![Windows 11](https://img.shields.io/badge/Windows%2011-%230079d5.svg?style=for-the-badge&logo=Windows%2011&logoColor=white)

Download .exe from releases here: https://github.com/bigsk1/airats/releases/tag/v1.0

You will most likely get a warning when trying to launch because it is not a signed .exe this is normal.

(optional)  build your own by cloning the win64 branch here:

```bash
git clone --single-branch --branch win64 https://github.com/bigsk1/airats.git
```
see the requirements.txt for what dependencies are needed

</br>

# Usage

## Linux

### Web Interface virtual environment in Python

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

## Command Line

</br>

Run any of the following commands from the airats directory:

python3 Main.py <image_url> [-w WIDTH] [-ht HEIGHT]

</br>

### Image size can be changed as needed

</br>

You can also run an image you have locally using:


python3 Main.py your_image.jpg -w 150 -ht 50

or 

python3 Main.py https://your-image-url.jpeg -w 150 -ht 50



```bash
python3 Main.py images/rat.jpg -w 50 -ht 25
```
</br>

Output image to a file
```bash
python3 Main.py images/rat.jpg -w 80 -o output.txt
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

![Rat Image](/images/rat.jpg)

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

<a href='https://github.com/bigsk1/airats/blob/master/LICENSE'>LICENSE</a>

This project is licensed under MIT License.
