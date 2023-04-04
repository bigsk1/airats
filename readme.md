# AIRATS

## ACSII Image Convertor
</br>
Into terminal

```bash
python3 Main.py rat.jpg -w 50 -ht 25
```
</br>

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

Turn any image locally or remotely into ASCII caractors.


## Linux Installation

```bash
git clone https://github.com/bigsk1/airats.git
```
```bash
cd airats
```
```bash
python Main.py rat.jpg -w 80 -o output.txt
```

Need to have installed 

python3

python3 -m pip install Pillow

python3 -m pip install requests

</br>

Supports 

    JPEG: .jpg, .jpeg
    PNG: .png
    GIF: .gif
    BMP: .bmp
    TIFF: .tif, .tiff
    ICO: .ico
    WebP: .webp

Image size can be changed if needed by using 

python3 Main.py your_image.jpg -w 150 -ht 50

or 

python3 Main.py https://your-image-url.jpeg -w 150 -ht 50

</br>

  ## License

This project is licensed under the MIT License.
