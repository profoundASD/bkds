// Get the current zoom level
var currentZoomLevel = 1.0; // 100%

// Set the new zoom level
var newZoomLevel = 0.9; // 90%

// Set the zoom level
document.body.style.zoom = newZoomLevel / currentZoomLevel;

//(function(){for(i=0;i<document.links.length;i++)document.getElementsByTagName("A")[i].parentNode.replaceChild("A", "SPAN");})();
  var link = document.createElement('link');
  link.rel = 'stylesheet';
  link.href = 'https://fonts.googleapis.com/icon?family=Material+Icons';
  document.head.appendChild(link);

  
  var node = document.querySelector('a'),
      newNode = document.createElement('span'),
      parent = node.parentNode,
      children = node.childNodes;
  
  Array.prototype.forEach.call(children, function (elem) {
      newNode.appendChild(elem);
  });
  parent.replaceChild(newNode, node);
  
  const nav_menu = document.getElementById('mw-navigation');  
  const page_base = document.getElementById('mw-page-base');
  const head_base = document.getElementById('mw-head-base');
  const toc = document.getElementById('toc');
  const notes = document.getElementById('Notes');
  const biblio = document.getElementById('Bibliography');
  const externalLinks = document.getElementById('External_links');
  const RefID = document.getElementById('References');
  const siteSub = document.getElementById('siteSub');
  const contentSub = document.getElementById('contentSub');
  const contentSub2 = document.getElementById('contentSub2');
  
  
  if( nav_menu !== null)
  {
      nav_menu.remove();
  }    
  if( page_base !== null)
  {
      page_base.remove();
  }
  
  if( head_base !== null)
  {
      head_base.remove();
  }
  if( toc !== null)
  {
      toc.remove();
  }    
  if( notes !== null)
  {
      notes.remove();
  }
  if( biblio !== null)
  {
      biblio.remove();
  }    
  if( externalLinks !== null)
  {
      externalLinks.remove();
  }
  if( RefID !== null)
  {   
      RefID.remove();
  }
  if( siteSub !== null)
  {  
      siteSub.remove();
  }
  if( contentSub !== null)
  {  
      contentSub.remove();
  }   
  if( contentSub2 !== null)
  {  
      contentSub2.remove();   
  }
  
  
  document.querySelectorAll('[role="note"]').forEach(function (el){
      el.remove();
      console.log('note removed...');
      });
      
  
  const reflist = document.getElementsByClassName('reflist-lower-alpha');
  while(reflist.length > 0){
      reflist[0].parentNode.removeChild(reflist[0]);
  }
  
  const references = document.getElementsByClassName('references');
  while(references.length > 0){
      references[0].parentNode.removeChild(references[0]);
  }
  
  const reference = document.getElementsByClassName('reference');
  while(reference.length > 0){
      reference[0].parentNode.removeChild(reference[0]);
  }
  
  
  const references_wrap = document.getElementsByClassName('mw-references-wrap');
  while(references_wrap.length > 0){
      references_wrap[0].parentNode.removeChild(references_wrap[0]);
  }
  
  
  const refbegin = document.getElementsByClassName('refbegin');
  while(refbegin.length > 0){
      refbegin[0].parentNode.removeChild(refbegin[0]);
  }
  
  const extText = document.getElementsByClassName('external text');
  while(extText.length > 0){
      extText[0].parentNode.removeChild(extText[0]);
  }
  
  // plainlinks metadata ambox ambox-content ambox-Refimprove
  const more_Citation = document.getElementsByClassName('box-More_citations_needed');
  while(more_Citation.length > 0){
      more_Citation[0].parentNode.removeChild(more_Citation[0]);
  }
  
  const mwEditSection = document.getElementsByClassName('mw-editsection');
  while(mwEditSection.length > 0){
      mwEditSection[0].parentNode.removeChild(mwEditSection[0]);
  }
  
  const excerpts = document.getElementsByClassName('rt-commentedText');
  while(excerpts.length > 0){
      excerpts[0].parentNode.removeChild(excerpts[0]);
  }
  
   

  const page_body_content = document.getElementById('mw-content-text');
  
  const image_tags = document.getElementsByTagName("img");


  
  var image_list='', feature_img='';
  let k=0;

  for (const image_tag of image_tags) {
    // Check the element's tag name
   // console.log('tagName: ', tag.tagName);
   console.log('checking: ', image_tag);
   console.log('checking inner html: ', image_tag.src.toString().toUpperCase());
   console.log(image_tag.src.toString().lastIndexOf("."), image_tag.src.toString().length);
  console.log(image_tag.src.toString().substring(image_tag.src.toString().lastIndexOf(".")+1, image_tag.src.toString().length).toUpperCase());
  let fileType = image_tag.src.toString().substring(image_tag.src.toString().lastIndexOf(".")+1, image_tag.src.toString().length).toUpperCase();
    let alt_text = image_tag.alt.toString();
    console.log("alt_text ", alt_text.toUpperCase());
    console.log("image_tag_parent: ", image_tag.parentElement.outerHTML);
   if( !(fileType ==('OGG') ) 
      && !( image_tag.src.toString().toUpperCase().includes("PROTECTED"))
      &&  !( image_tag.src.toString().toUpperCase().includes("PROTECTION"))
      &&  !( image_tag.src.toString().toUpperCase().includes("PENDING"))
      &&  !( image_tag.src.toString().toUpperCase().includes("FEATURED"))
      &&  !( image_tag.src.toString().toUpperCase().includes("LISTEN"))
      &&  !(alt_text.toUpperCase().includes("FEATURED"))
      &&  !(alt_text.toUpperCase().includes("LISTEN"))
      &&  !(image_tag.src.toString().toUpperCase().includes("SYMBOL"))
      &&  (image_tag.parentElement.outerHTML.includes(":"))
      &&  !(image_tag.src.toString().toUpperCase().includes("QUESTION_BOOK"))
      &&  !(image_tag.src.toString().toUpperCase().includes("WIKI_LETTER"))
      &&  !(image_tag.src.toString().toUpperCase().includes("TEXT_DOCUMENT"))
      &&  !(image_tag.src.toString().toUpperCase().includes("QUESTION_MARK"))
      &&  !(image_tag.src.toString().toUpperCase().includes("EMBLEM-MONEY"))
      &&  !(image_tag.alt.toString().toUpperCase().includes("ICON"))
      &&  !(image_tag.src.toString().toUpperCase().includes("RED_PENCIL"))
      &&  !(image_tag.parentElement.outerHTML.toString().toUpperCase().includes("PORTAL:TECHNOLOGY"))
      &&  !(image_tag.parentElement.outerHTML.toString().toUpperCase().includes("STATIC/IMAGES"))

      )  
      

      {
        image_tag.classList.add("mySlides2");
        image_tag.classList.add("fade2");
        image_tag.classList.add("dot2");
        console.log('image_tag9999: ' , image_tag);
        console.log('image_tag9999: ' , image_tag.title);

        image_list+='<div>'+image_tag.outerHTML+'</div>';
        if(k==0){
            let iframe_jpg=image_tag.innerText;
            console.log(image_tag.outerHTML);
            console.log('image_tag.innerText', image_tag.innerText);

            console.log('image_list', image_list);
            console.log('image_tag.parentElement.outerHTML; ', image_tag.parentElement.outerHTML);
            good_part = image_tag.parentElement.outerHTML.split(':')[1].split('"')[0];
            console.log('good_part: ', good_part.trim());        //console.log(image_tag.parentElement.outerHTML.split(':')[1].substring(0, split_index));
            console.log('image_alt ', image_tag.alt.replaceAll(" ", "_"));
            if(!good_part.includes('none;')){
                feature_img = window.location.href + '#/media/File:' + good_part.trim().replaceAll(" ", "_");

                feature_img=`                             
                                    <div class="iframe-container" style="margin-left:-5%; margin-top:-1%;">       
                                    <div class="overlay3"></div>
                                        <iframe   sandbox="allow-forms allow-scripts allow-same-origin"
                                                 id="wiki_iframe" scrolling="no" height="1000" width="1000" src="`+feature_img+`"> 

                                        </iframe>
                                        <div class="overlay"><div class="overlay1">

                                        </div><div>
                                        
                                        <div class="overlay2"></div>

                                    </div>


                            ` ;
                

            }else
            {
            feature_img= "<div background-image:url('"+chrome.runtime.getURL('Wiki.jpg');
            feature_img+="></div>";
                
            }
            console.log('feature_img: ', feature_img);
            
        }
        k++;
   }
   
  
  }
  image_list+= '<div style="padding-top:20%;" class="mySlides dot fade">The End</div>';
  
  const title_tag = document.getElementById("firstHeading");
  page_title= title_tag.innerText;

  const p_tags = page_body_content.querySelectorAll("p, h3, b");
  
  
  var tag_list='';
  
  var i=0;
  for (const tag of p_tags) {

      if(tag.innerText.length > 100 && !(tag.innerHTML.toUpperCase().includes('ABOUT THIS SOUND')) )
      {
          i++;
          tag_list+='<div id="read-aloud-body" class="mySlides fade" id="parabreak"><span id="read-aloud-body" style="margin-top:-5%" class="dot">'+tag.innerHTML+'<span><br><br>'+
          '<div style="float:left; padding-bottom:5%;"><b>Part '+i+' of '+p_tags.length+'</b></div></div>'
      }
  }
  tag_list+= '<div id="read-aloud-body" style="padding-top:30%; font-size:2.5em; color:rgb(30, 29, 29, .7); text-align:center;" class="mySlides dot fade"><b>The End<br><span style="font-size:.25em">Touch NEXT to continue</span><br><span style="font-size:.25em">or wait for player to restart</span></b><br><br></div>';  
  

  
  document.body.innerHTML=`                          

                          <div style="float:left; top:5%;">

                                    <div id="content-wrapper-left-top" style=" text-align:left; 
                                        top: 0; left: 0;  width: 35%; background-color: #D3D3D3; 
                                        color: black; ">

                                        <div style="background-color:black; color: white; height:5%; top:0; left: 0; width:100%; padding-top:1%; padding-left:2%; float:left;">
                                        <button onclick="history.back()">
                                        <i style="font-size: 36px; padding-right:1.5%;" class="material-icons">arrow_back</i>
                                        </button>
                                        <button onclick="history.forward()">
                                        <i style="font-size: 36px; padding-right:1.5%;" class="material-icons">arrow_forward</i>
                                        </button >
                                        <button onclick="window.location.reload();">
                                        <i style="font-size: 36px; padding-right:1.5%;" class="material-icons">refresh</i>
                                        </button>
                                        <button onclick="window.location.href='http://localhost/html/main/?playAnimation=true';">
                                        <i style="font-size: 36px; padding-right:1.5%;" class="material-icons">home</i>
                                        </button>
                                        <div style="font-size:1.5em; padding-left:55%;">
                                        <div style="float:left; margin-top:-12%;">

                                            <i style="color:white; float:left; padding-right:5px;">Wikipedia Summary</i>
                                            <img style="width:25px; margin-top:-3%;" src=` +chrome.runtime.getURL('Wiki.jpg')+`>
                                        </div>
                                       
                                        </div>
                                        </div>

                                        
                                        <div style="text-align:left; font-size:2.5em;  padding-top:10%; padding-left:3%;">
                                            <b>`+page_title+`</b>
                                        </div>
                                    
                                    <div class="touch_and_speak" style="font-size:2em; padding-right:5%; padding-left:3%; margin-top:-2%;">`+tag_list+`
                                    </div>

                            </div>
                            <div id="content-wrapper-left-bottom" style="width:35%; text-align:left;">  
                                  <div style="padding-top:1.5%; padding-left:5%; font-size:2em;">
                                      <button id="slideNavLeft" class="box">
                                                  <div  style="font-size:2em;">BACK</div>
                                      </button>
  
  
                                      <button  id="slideNavStop" class="box" style="background-color:#800101; color:white;">
                                                  <div  style="font-size:2em;">STOP</div>
                                      </button>
                                      <button  id="slideNavListen" class="box" style="background-color:#008024; color:white; ">
                                                  <div  style="font-size:2em; text-align:center; margin-left:-6%; ">LISTEN</div>
                                      </button>                                   
  
                                      <button id="slideNavRight" class="box">                                                
              
                                                  <div  style="font-size:2em; ">NEXT</div>
                                      </button>
  
                                      
                                    </div>
                                </div>
                            </div>
                            <div >
                                <div id="content-wrapper-right" style=" text-align:center; padding-left:3%;  width: 60%; height:100%; color: black; ">
       
                                <div id="content-wrapper-right" style=" text-align:center; padding-left:3%; width: 60%; height:100%; color: black; ">
                                        <div >`+feature_img+`
                                        </div>
                                        <div class="overlay" ></div>
                                </div>
                            </div>
                            <div id="furthest">
                                <div id="content-wrapper-far-right" style="text-align:center; top: 0; right:0; padding-top:33%; width: 5%; height:100%; ">
                                    <button id="refresh_box"  style="background-color:black; border: none; color:blue; width:100px; height:100px; padding-right:30%; text-align:center;">
                                       <img height="100" width="100" src=` +chrome.runtime.getURL('Refreshgrey.jpg')+
                                       `></span>
                                     </button>
                                </div>
                            </div>

                            `;
  
  


  const myDiv = document.getElementById("content-wrapper-right");
  /*
  
  document.addEventListener('mousedown', () => {
    document.querySelectorAll('body').forEach(el => {
    var high_el = document.getElementById("high_span");
  
    
    //console.log(getSelection().anchorNode.text);
  
    if(high_el !== null)
    {
        high_el.classList.remove("highlight");
        high_el.id = "";
    }
    
    });
  });
  
  
  */
  
var links = document.getElementsByTagName("a");

// Loop through all the links
for (var i = 0; i < links.length; i++) {
  // Add a style to each link
  links[i].classList.add("default");
}
  
  const change = src => {
	document.getElementById('main').src = src
    console.log('executed_change');
}


(
    function()
      {
          for(i=0;i<document.links.length;i++)
          {
              
              if (document.getElementsByTagName("A")[i].innerHTML.includes('image')){
                  document.getElementsByTagName("A")[i].removeAttribute("href");
              }
              document.links[i].style.borderWidth='1px';
              document.links[i].style.borderStyle='solid';
              document.links[i].style.color='blue';
              document.links[i].style.backgroundColor='#b8b8bd';
          }
      }
  )();



