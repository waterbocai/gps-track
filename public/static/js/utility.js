/*
 * jquery-counter plugin
 *
 * Copyright (c) 2009 Martin Conte Mac Donell <Reflejo@gmail.com>
 * Dual licensed under the MIT and GPL licenses.
 * http://docs.jquery.com/License
 */
/** 
*删除数组指定下标或指定对象 
*/ 
Array.prototype.remove=function(obj){ 
    for(var i =0;i <this.length;i++){ 
        var temp = this[i]; 
        if(!isNaN(obj)){ 
            temp=i; 
        } 
        if(temp == obj){ 
            for(var j = i;j <this.length;j++){ 
                this[j]=this[j+1]; 
            } 
            this.length = this.length-1; 
        } 
    } 
}

 
function date2str(yy, mm, dd, prenext) {
    var s, d, t, t2;
    t = Date.UTC(yy, mm, dd);
    t2 = 1 * 1000 * 3600 * 24; //加减1天的时间
    if (prenext == 'pre') {
        t-= t2;
    } else {
        t+= t2;
    }
    d = new Date(t);

    s = d.getUTCFullYear() + "-";
    s += ("00"+(d.getUTCMonth()+1)).slice(-2) + "-";
    s += ("00"+d.getUTCDate()).slice(-2);

    return s;
}

function str2date(str, prenext){   
  var   dd, mm, yy;   
  var   reg = /^(\d{4})-(\d{1,2})-(\d{1,2})/;
  str = LTrim(RTrim(str))
  if (arr = str.match(reg)) {
    yy = Number(arr[1]);
    mm = Number(arr[2])-1;
    dd = Number(arr[3]);
  } else {
    var d = new Date();
    yy = d.getUTCFullYear();
    mm = ("00"+(d.getUTCMonth())).slice(-2);
    dd = ("00"+d.getUTCDate()).slice(-2);
  }
 if (prenext == null || (prenext != 'pre' && prenext != 'next')) {
    var prenext = 'pre';
  }

  var d = date2str(yy, mm, dd, prenext);
  return d;
}

function LTrim(str){ 
    var i; 
    for(i=0;i<str.length;i++){
        if(str.charAt(i)!=" ") 
            break; 
    } 
    str = str.substring(i,str.length); 
    return str; 
}
function RTrim(str){ 
    var i; 
    for(i=str.length-1;i>=0;i--){ 
        if(str.charAt(i)!=" ") 
            break; 
    } 
    str = str.substring(0,i+1); 
    return str; 
}
function Trim(str){ 

return LTrim(RTrim(str)); 

} 
// 对Date的扩展，将 Date 转化为指定格式的String   
// 月(M)、日(d)、小时(h)、分(m)、秒(s)、季度(q) 可以用 1-2 个占位符，   
// 年(y)可以用 1-4 个占位符，毫秒(S)只能用 1 个占位符(是 1-3 位的数字)   
// 例子：   
// (new Date()).Format("yyyy-MM-dd hh:mm:ss.S") ==> 2006-07-02 08:09:04.423   
// (new Date()).Format("yyyy-M-d h:m:s.S")      ==> 2006-7-2 8:9:4.18 
Date.prototype.format = function(format)
{
    var o = {
    "M+" : this.getMonth()+1, //month
    "d+" : this.getDate(),    //day
    "h+" : this.getHours(),   //hour
    "m+" : this.getMinutes(), //minute
    "s+" : this.getSeconds(), //second
    "q+" : Math.floor((this.getMonth()+3)/3),  //quarter
    "S" : this.getMilliseconds() //millisecond
    }
    if(/(y+)/.test(format))
    {
        format=format.replace(RegExp.$1,(this.getFullYear()+"").substr(4 - RegExp.$1.length));
    }
    for(var k in o)
    {
        if(new RegExp("("+ k +")").test(format))
       {
           format = format.replace(RegExp.$1,RegExp.$1.length==1 ? o[k] : ("00"+ o[k]).substr((""+ o[k]).length));
      }
    }
    return format;
}

/* 
* 获得时间差,时间格式为 年-月-日 小时:分钟:秒 或者 年/月/日 小时：分钟：秒 
* 其中，年月日为全格式，例如 ： 2010-10-12 01:00:00 
* 返回精度为：秒，分，小时，天
*/

function GetDateDiff(startTime, endTime, diffType) {
    var sTime,eTime;
    //将xxxx-xx-xx的时间格式，转换为 xxxx/xx/xx的格式 
    if (typeof(startTime)=="string") {
        startTime = startTime.replace(/\-/g, "/");
        sTime =new Date(startTime); //开始时间
    } else {
        sTime = startTime       
    }
    
    if (typeof(endTime)=="string"){
        endTime = endTime.replace(/\-/g, "/");
        eTime =new Date(endTime); //结束时间  
    } else {
        eTime = endTime
    }
    //将计算间隔类性字符转换为小写
    diffType = diffType.toLowerCase();
    var sTime =new Date(startTime); //开始时间
    var eTime =new Date(endTime); //结束时间
    //作为除数的数字
    var divNum =1;
    switch (diffType) {
        case"second":
            divNum =1000;
            break;
        case"minute":
            divNum =1000*60;
            break;
        case"hour":
            divNum =1000*3600;
            break;
        case"day":
            divNum =1000*3600*24;
            break;
        default:
            break;
    }
    return parseInt((eTime.getTime() - sTime.getTime()) / parseInt(divNum));
}

function addDate(startTime, num, nType) {
    //将xxxx-xx-xx的时间格式，转换为 xxxx/xx/xx的格式 
    startTime = startTime.replace(/\-/g, "/");
    //将计算间隔类性字符转换为小写
    nType = nType.toLowerCase();
    var sTime =new Date(startTime); //开始时间
    //作为转换单位的数字
    var divNum =1;
    switch (nType) {
        case"second":
            divNum =1000;
            break;
        case"minute":
            divNum =1000*60;
            break;
        case"hour":
            divNum =1000*3600;
            break;
        case"day":
            divNum =1000*3600*24;
            break;
        default:
            break;
    }
    var d = new Date();
    d.setTime(sTime.getTime()+num*divNum); 
    return d.format('yyyy-MM-dd hh:mm:ss');
}
//返回没有格式化的js时间对象
function addDate2(startTime, num, nType) {
    var sTime;
    if (typeof(startTime)=="string"){
        //将xxxx-xx-xx的时间格式，转换为 xxxx/xx/xx的格式 
        startTime = startTime.replace(/\-/g, "/");
        //将计算间隔类性字符转换为小写
        nType = nType.toLowerCase();
        sTime =new Date(startTime); //开始时间
    } else {
        sTime = startTime
    }
    
    //作为转换单位的数字
    var divNum =1;
    switch (nType) {
        case"second":
            divNum =1000;
            break;
        case"minute":
            divNum =1000*60;
            break;
        case"hour":
            divNum =1000*3600;
            break;
        case"day":
            divNum =1000*3600*24;
            break;
        default:
            break;
    }
    var d = new Date();
    d.setTime(sTime.getTime()+num*divNum); 
    return d;
}

//将"08:37 下午"的时间格式，转换为24小时制 "20:37:00"
function uniformTime(str)
{
    var t = str.split(" ");
    var hm = t[0].split(":")
    if (hm.length==3){
        //已经是标准格式的时间
        return str;
    }
    var h = parseInt(hm[0]);
    if (t[1]=='下午'){
        h = h+12
    }
    return h.toString()+':'+hm[1]+':00'
}

function iconObj() {
    var arr = {
        'busmap':{
            'url':"/static/img/busmapicon.png",
            'anchor':[1,1,0],
            'xSum':9,
            'ySum':1,
            'width':31,
            'height':35,
        },
        'busmap_noshadow':{
            'url':"/static/img/busmapicon_noshadow.png",
            'anchor':[1,1,0],
            'xSum':9,
            'ySum':1,
            'width':31,
            'height':35,        
        },
        'num_shadow':{
            'url':"/static/img/marker4.png",
            'anchor':[1],
            'xSum':2,
            'ySum':11,
            'width':31,
            'height':35,
        },
        'num':{
            'url':"/static/img/num_icons.png",
            'anchor':[1],
            'xSum':2,
            'ySum':11,
            'width':31,
            'height':35,        
        },
    }
    return arr;
}

function getMarkerImage(name){
    if (name=="") {
        name = "motor"
    }
    var icon= new qq.maps.MarkerImage(
                "/static/img/map_"+name+".png",
                new qq.maps.Size(31, 35),
                new qq.maps.Point(0, 0),
                new qq.maps.Point(16, 35)
    )
    return icon;
}    

function getMarkerIcon(name){   
    if (name=="") {
        name = "motor"
    }
    var icon= new qq.maps.MarkerImage(
        "/static/img/map/"+name+".png",
        new qq.maps.Size(31, 40),
        new qq.maps.Point(0, 0),
        new qq.maps.Point(16, 40)
    )
    return icon;
}

function qqParseIcon(iType,sX,num) {
   var iconArr = iconObj();
    myIcon = iconArr[iType]
    var width  = myIcon['width'];
    var height = myIcon['height'];
    var iconArr =[];
    
    var anchorY = height;
    var anchorP;//锚点位置参数 
    for (var x = 0; x < myIcon['xSum']; x++) {
        var arr = []
        anchorP = (x< myIcon['anchor'].length) ? myIcon["anchor"][x] : anchorP ;
        anchorX = anchorP*width/2

        for (var y=0;y<myIcon['ySum'];y++){         
            arr.push(new qq.maps.MarkerImage(
                myIcon['url'],
                new qq.maps.Size(width, height),
                new qq.maps.Point(x*width, 0),
                new qq.maps.Point(anchorX, anchorY)
            ));            
        }
        iconArr.push(arr)
    }
    return iconArr;
};

