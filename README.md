# Anaranjado
![Anaranjado](https://scontent-eze1-1.xx.fbcdn.net/v/t1.0-9/18739918_10213115697786060_6279067385623231756_n.jpg?oh=dd7fcad91a43f6d8198b077be63f214d&oe=59B3895C)


<b>Introduction</b>

When security tools crawls for links within target applications, there are some restrictions while parsing JavaScript files. In specific, during many
pentest projects it was seen that some links were hardcoded within JavaScript files, but scanners aren't able to find them.

For example, considering the following HTML file:
</br>\<html>
</br>\<body><script src="thisIsTest.js"></script>
\<a href="`www.google.com.ar`"> Google! \</a>
</br>\</body>
</br>\</html>

And the referenced JavaScript file (thisIsTest.js) is the following:</br>
public void thest(){ </br>
&emsp;	page = "`http://www.Encontrame.com.ar`"; </br>
&emsp;	for(1;99;){ </br>
&emsp;&emsp;		page2 = "/foundme.asp"; </br>
&emsp;	} </br>
&emsp;	page34="`http:%2f%2fencontrame2.com%2ftest%3fa%3d2`"; </br>
&emsp;	if s == 3{ </br>
&emsp;&emsp;		line = "jojo"; </br>
&emsp;	} </br>
&emsp;	page55="`http%3a%2f%2fencontrame3.com%2ftest%3fa%3d2`"; </br>
&emsp;	while (2){ </br>
&emsp;&emsp;		do something </br>
&emsp;	} </br>
&emsp;	redirect = "/foundme2.asp?a=33"; </br>
} </br>

By using Burp to spider the site, the following result was achieved: </br>
[+] `http://localhost` </br>
&emsp;	- craul	</br>
&emsp;&emsp;		- index.html </br>
&emsp;&emsp;		- thisIsTest.js </br>
[+] `http://www.encontrame.com.ar` </br>

By crawling the page using Arachni, the following result was achieved: </br>
 [+] `http://localhost/craul/index.html` </br>
 [+] `http://localhost/craul/thisIsTest.js` </br>
 [+] `http://localhost/craul/www.google.com.ar` </br>

While using <b>`Anaranjado`</b>, the following result was achieved: </br>
[i]- Hey! This is good, some links were found within JavaScript Files: </br>
`http://encontrame2.com/test?a=2` From: `http://localhost/craul/thisIsTest.js` </br>
`/foundme.asp` From: `http://localhost/craul/thisIsTest.js` </br>
`http://encontrame3.com/test?a=2` From: `http://localhost/craul/thisIsTest.js` </br>
`http://www.Encontrame.com.ar` From: `http://localhost/craul/thisIsTest.js` </br>
`/foundme2.asp?` From: `http://localhost/craul/thisIsTest.js` </br>

</br>

<b>Summary</b> </br>
Anaranjado is a scraping tool that identifies URLs within JavaScript files.

</br>

<b>Usage</b> </br>
In order to identify JavaScript referenced files within an HTML file, run the following command: </br>
&emsp; `python Anaranjado.py --url http://localhost/`

The tool will retrieve all .js files and then will perform scraping to each one. The final result will be a list of identified links within JavaScript files.

In order to scrap a single JavaScript file, run the following command: </br>
&emsp; `python Anaranjado.py --jsUrl http://localhost/craul/thisIsTest.js`

</br>

<b>Coming</b>
Anaranjado is still being developed and this will be happening soon:
- Bug fixing
- False positive improvement
- Regex enhancement
- New funtionalities
- Threading
- Full Crawling
