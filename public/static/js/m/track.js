
\$(document).ready(function(){ 
     \$('#radio_last_hour').click(function(e){
         \$('#hours-select').show();
         \$('#history-select').hide();
     });
     \$('#radio_selfdefine').click(function(e){
         \$('#hours-select').hide();
         \$('#history-select').show();
     });
     
     \$('#history-map').click(function(e) {
         duUrl = trackDuration();
         url= "/m/bustrack?act=HISTORY-TRACK"+duUrl
         window.location.href=url
         //href="/m/bustrack?act=HISTORY-STAT&imei=862304020534585&wdate=2015-03-10" target='_blank' 
     });
     
     \$('#history-stat').click(function(e) {
         duTime = trackDuration();
         url= "/m/bustrack?act=HISTORY-STAT"+duUrl
         window.location.href=url
         //href="/m/bustrack?act=HISTORY-STAT&imei=862304020534585&wdate=2015-03-10" target='_blank'  
     });
     
     function trackDuration(){
         var startDatetime,endDatetime;
         //获取时间设置模式
         var selType = \$( "[name='radio-select']:checked" ).attr( "id" )
         //最近过去的时间 选择模式
         if (selType=='radio_last_hour'){
             _hour = \$("#hours-menu option:selected").val();
             endDatetime= new Date();
             endDatetime=endDatetime.format('yyyy-MM-dd hh:mm:ss')
             startDatetime=addDate(endDatetime,parseInt('-'+_hour),'hour');
         } else {
             _startDate = \$("#start_date").val();
             _startTime = uniformTime(\$("#start_time").val());
             _endDate = \$("#end_date").val();
             _endTime = uniformTime(\$("#end_time").val());
             if (_startDate==""){
                 \$("#start_date").focus()
                 alert("开始日期不能为空");
             }
             
             if (_startTime==""){
                 \$("#start_time").focus()
                 alert("开始时间不能为空");
             }
             if (_endDate==""){
                 \$("#end_date").focus()
                 alert("结束日期不能为空");
             }
             
             if (_endTime==""){
                 \$("#end_time").focus()
                 alert("结束时间不能为空");
             }
             
             startDatetime = _startDate +' ' + _startTime
             endDatetime = _endDate +' ' + _endTime
             var dh = GetDateDiff(startDatetime,endDatetime,'hour')
             if (dh>48) {
                 alert('时间间隔不能超过48小时，请重新选择')
             }
         }
         //alert(startDatetime)
         return "&imei="+imei+"&startTime="+startDatetime+"&endTime="+endDatetime
     }
 });
