
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
         //��ȡʱ������ģʽ
         var selType = \$( "[name='radio-select']:checked" ).attr( "id" )
         //�����ȥ��ʱ�� ѡ��ģʽ
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
                 alert("��ʼ���ڲ���Ϊ��");
             }
             
             if (_startTime==""){
                 \$("#start_time").focus()
                 alert("��ʼʱ�䲻��Ϊ��");
             }
             if (_endDate==""){
                 \$("#end_date").focus()
                 alert("�������ڲ���Ϊ��");
             }
             
             if (_endTime==""){
                 \$("#end_time").focus()
                 alert("����ʱ�䲻��Ϊ��");
             }
             
             startDatetime = _startDate +' ' + _startTime
             endDatetime = _endDate +' ' + _endTime
             var dh = GetDateDiff(startDatetime,endDatetime,'hour')
             if (dh>48) {
                 alert('ʱ�������ܳ���48Сʱ��������ѡ��')
             }
         }
         //alert(startDatetime)
         return "&imei="+imei+"&startTime="+startDatetime+"&endTime="+endDatetime
     }
 });
