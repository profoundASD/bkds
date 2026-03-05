// Hard-coded values
const extBuildNum = "0033"
const uiBuildNum = "0017";
const extBuildDate = '10/04/2023 11:54:03:01 UTC';
const uiBuildDate ='07/21/2023 12:01:03:01 UTC';

// Find the HTML elements with the IDs "element1" and "element2"
const element1 = document.getElementById("extBuild");
const element2 = document.getElementById("uiBuild");
const element3 = document.getElementById("extBuildDate");
const element4 = document.getElementById("uiBuildDate");

element1.innerHTML = extBuildNum;
element2.innerHTML = uiBuildNum;
element3.innerHTML = extBuildDate;
element4.innerHTML = uiBuildDate;
