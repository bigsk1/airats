# AIRATS
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![Windows 11](https://img.shields.io/badge/Windows%2011-%230079d5.svg?style=for-the-badge&logo=Windows%2011&logoColor=white)
## ASCII Image Convertor

A simple Flask web app  to generate ASCII art from an image URL

works in powershell or terminal / command prompt also! 
 
</br>
</br>

![fish](/images/fish.jpg)

</br>

# Installation

Download the win64 version from releases

Extract the zip to a folder

Double click the app.exe inside the airats-win64 folder to launch it. 

Open a web browser and visit [http://localhost:8081] or (http://127.0.0.1:8081) to access the app.

</br>

** Folder should contain all dependency's needed but you may need to  [install python](https://www.python.org/downloads/windows/
)  
</br>

## Command Line

</br>

build your own by cloning the win64 branch here:

![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white)

```bash
git clone --single-branch --branch win64 https://github.com/bigsk1/airats.git
```

```bash
cd airats
```

```bash
python3 Main.py images/rat.jpg -w 50 -ht 25
```
output in terminal 
```bash
D:\github_airats\airats-win64> python3 Main.py images/rat.jpg -w 50 -ht 25


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
```

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

</br>

## Terminal

![Windows Terminal](https://img.shields.io/badge/Windows%20Terminal-%234D4D4D.svg?style=for-the-badge&logo=windows-terminal&logoColor=white)

```bash
python3 Main.py images/rat.jpg -w 50 -ht 25
```

## Build the app
see requirements.txt for dependency's

</br>

```bash
pip install -r requirements.txt
```

```bash
python3 setup.py build
```

```bash 
cd build\exe.win-amd64-3.10  
```
( or whatever your new folder is )

```bash
.\app.exe
```


Supports 

    JPEG: .jpg, .jpeg
    PNG: .png
    GIF: .gif
    BMP: .bmp
    TIFF: .tif, .tiff
    ICO: .ico
    WebP: .webp



</br>

  <a href='https://github.com/bigsk1/airats/blob/master/LICENSE'>LICENSE</a>

This project is licensed under MIT License.
