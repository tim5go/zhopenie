# Chinese Open Information Extraction (Zhopenie)

## Installation
This module makes heavily use of pyltp
1. Install pyltp
    ```
    pip install pyltp
    ```
2. Download NLP model from [百度雲](http://pan.baidu.com/share/link?shareid=1988562907&uk=2738088569#list/path=%2F)
 

## Usage
The extractor module tries to break down a Chinese sentence into a Triple relation (e1, e2, r), which can be understood by computer  <br />
e.g. 星展集团是亚洲最大的金融服务集团之一, 拥有约3千5百亿美元资产和超过280间分行, 业务遍及18个市场。 <br />
are parsed as follows:  <br /> <br />
e1:星展集团, e2:亚洲最大的金融服务集团之一, r:是  <br />
e1:星展集团, e2:约3千5百亿美元资产, r:拥有  <br />
e1:业务, e2:18个市场, r:遍及  <br /> <br />

However, this extractor is about ~70% accurate and is still under improvement at this moment. Feel free to comment and make pull request. <br /> <br />


## Credits
哈工大社会计算与信息检索研究中心研制的语言技术平台 [LTP](https://github.com/HIT-SCIR/ltp)
