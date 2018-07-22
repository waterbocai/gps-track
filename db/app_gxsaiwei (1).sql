-- phpMyAdmin SQL Dump
-- version 4.0.10deb1
-- http://www.phpmyadmin.net
--
-- 主机: localhost
-- 生成日期: 2016-06-07 22:02:07
-- 服务器版本: 5.5.49-0ubuntu0.14.04.1-log
-- PHP 版本: 5.5.9-1ubuntu4.16

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;

--
-- 数据库: `app_gxsaiwei`
--

-- --------------------------------------------------------

--
-- 表的结构 `Account`
--

DROP TABLE IF EXISTS `Account`;
CREATE TABLE IF NOT EXISTS `Account` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Customer_openid` text NOT NULL COMMENT '微信openid',
  `iwaiter_money` int(11) NOT NULL COMMENT '慧特币',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- 表的结构 `BackgroudTaskSequence`
--

DROP TABLE IF EXISTS `BackgroudTaskSequence`;
CREATE TABLE IF NOT EXISTS `BackgroudTaskSequence` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text COMMENT '任务名称',
  `param` text NOT NULL COMMENT '任务参数',
  `create_at` datetime NOT NULL,
  `owner` text NOT NULL COMMENT '任务提交人openid',
  `state` text NOT NULL COMMENT '完成情况：waiting,complete,working',
  `start_at` datetime DEFAULT NULL COMMENT '任务启动时间',
  `finished_at` datetime DEFAULT NULL COMMENT '完成时间',
  `report_origin` text NOT NULL COMMENT '报表数据来源: adapter-适配器自动统计',
  PRIMARY KEY (`id`),
  KEY `create_at` (`create_at`),
  KEY `start_at` (`start_at`),
  KEY `finished_at` (`finished_at`),
  KEY `create_at_2` (`create_at`),
  KEY `start_at_2` (`start_at`),
  KEY `finished_at_2` (`finished_at`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2232 ;

-- --------------------------------------------------------

--
-- 表的结构 `BusLine`
--

DROP TABLE IF EXISTS `BusLine`;
CREATE TABLE IF NOT EXISTS `BusLine` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `busgroupid` int(11) NOT NULL COMMENT '车队id，对应tianwangshouhu_DeviceGroup_id',
  `from_name` text NOT NULL COMMENT '起始站点',
  `to_name` text NOT NULL COMMENT '终点站名称',
  `created_at` datetime NOT NULL,
  `openid` text NOT NULL,
  `company_id` int(11) NOT NULL COMMENT '所属公司',
  `mileage` float NOT NULL DEFAULT '0' COMMENT '起始站点直线距离，单位公里',
  PRIMARY KEY (`id`),
  KEY `busgroupid` (`busgroupid`),
  KEY `created_at` (`created_at`),
  KEY `mileage` (`mileage`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=26 ;

-- --------------------------------------------------------

--
-- 表的结构 `BusTravel`
--

DROP TABLE IF EXISTS `BusTravel`;
CREATE TABLE IF NOT EXISTS `BusTravel` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_time` datetime NOT NULL COMMENT '开始时间',
  `to_time` datetime NOT NULL COMMENT '结束时间',
  `duration_gmileage` float NOT NULL COMMENT '行程里程',
  `imei` text,
  `from_site_id` int(11) DEFAULT '0',
  `to_site_id` int(11) DEFAULT '0',
  `num_seated` int(11) DEFAULT '0',
  `num_unseated` int(11) DEFAULT '0',
  `num_unknown` int(11) DEFAULT '0',
  `num_timeout` int(11) DEFAULT '0',
  `type` text,
  `mileage_seated` float DEFAULT '0',
  `mileage_unseated` float DEFAULT '0',
  `mileage_unknown` float DEFAULT '0',
  `mileage_timeout` float DEFAULT '0',
  `create_at` datetime DEFAULT NULL,
  `busline_id` int(11) NOT NULL COMMENT '班车线路id',
  `report_state` text CHARACTER SET utf8 NOT NULL COMMENT 'wait-等待出报告，working-正在出报告，finish-已经完成',
  `report_start_at` datetime DEFAULT NULL COMMENT '报告开始时间',
  `report_finish_at` datetime DEFAULT NULL COMMENT '报告结束时间',
  `seated_checked` int(11) NOT NULL COMMENT '核对的人数',
  `fee` int(11) NOT NULL COMMENT '总金额',
  `fee_checked` int(11) NOT NULL COMMENT '核对的总金额',
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`),
  KEY `to_time` (`to_time`),
  KEY `from_time_2` (`from_time`),
  KEY `to_time_2` (`to_time`),
  KEY `from_site_id` (`from_site_id`),
  KEY `to_site_id` (`to_site_id`),
  KEY `create_at` (`create_at`),
  KEY `report_start_at` (`report_start_at`),
  KEY `report_finish_at` (`report_finish_at`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=latin1 AUTO_INCREMENT=1225 ;

-- --------------------------------------------------------

--
-- 表的结构 `CacheSeat`
--

DROP TABLE IF EXISTS `CacheSeat`;
CREATE TABLE IF NOT EXISTS `CacheSeat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_at` datetime NOT NULL COMMENT '上报时间',
  `seatStatus` text NOT NULL COMMENT '座位状态',
  `imei` text NOT NULL COMMENT '设备imei',
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `report_at` (`report_at`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='对上报的数据进行缓存' AUTO_INCREMENT=5936942 ;

-- --------------------------------------------------------

--
-- 表的结构 `CacheSeat2`
--

DROP TABLE IF EXISTS `CacheSeat2`;
CREATE TABLE IF NOT EXISTS `CacheSeat2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `report_at` datetime NOT NULL COMMENT '上报时间',
  `seatStatus` text NOT NULL COMMENT '座位状态',
  `imei` text NOT NULL COMMENT '设备imei',
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `report_at` (`report_at`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 COMMENT='对上报的数据进行缓存' AUTO_INCREMENT=22809 ;

-- --------------------------------------------------------

--
-- 表的结构 `CmdLog`
--

DROP TABLE IF EXISTS `CmdLog`;
CREATE TABLE IF NOT EXISTS `CmdLog` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `cmd` text NOT NULL COMMENT '下发命令',
  `create_at` datetime NOT NULL,
  `openid` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `create_at` (`create_at`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `openid` (`openid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=26543 ;

-- --------------------------------------------------------

--
-- 表的结构 `Company`
--

DROP TABLE IF EXISTS `Company`;
CREATE TABLE IF NOT EXISTS `Company` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text COMMENT '真实姓名',
  `idCard` text,
  `idAddr` text COMMENT '身份证地址',
  `workAddr` text COMMENT '工作地点',
  `account` int(11) DEFAULT NULL COMMENT '销售收入',
  `weixin` text,
  `qq` int(11) DEFAULT NULL,
  `phone` text COMMENT '联系手机号码',
  `weixinpay_account` text COMMENT '微信支付账号',
  `alipay` text COMMENT '支付宝支付账号',
  `updstributor_id` int(11) DEFAULT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL,
  `WeixinQRcodeScene_id` int(11) DEFAULT NULL,
  `created_at` datetime NOT NULL,
  `valid` text NOT NULL COMMENT '是否有效：有效/失效',
  `confirmed_at` datetime DEFAULT NULL COMMENT '用户确认的日期，也就是授权成功的日期',
  `regedit_openid` text NOT NULL,
  `company` text,
  `owner_openid` text COMMENT '确认用户openid',
  PRIMARY KEY (`id`),
  KEY `updstributor_id` (`updstributor_id`),
  KEY `WeixinQRcodeScene_id` (`WeixinQRcodeScene_id`),
  KEY `created_at` (`created_at`),
  FULLTEXT KEY `idCard` (`idCard`),
  FULLTEXT KEY `province` (`province`),
  FULLTEXT KEY `owner_openid` (`owner_openid`),
  FULLTEXT KEY `regedit_openid` (`regedit_openid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;

-- --------------------------------------------------------

--
-- 表的结构 `CompanyHasEmployee`
--

DROP TABLE IF EXISTS `CompanyHasEmployee`;
CREATE TABLE IF NOT EXISTS `CompanyHasEmployee` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openid` text NOT NULL COMMENT '微信openid',
  `company_id` int(11) NOT NULL COMMENT '公司id',
  `privilege` text NOT NULL COMMENT '权限：guest，manager',
  `create_at` datetime NOT NULL COMMENT '入职日期',
  `range` text COMMENT '经销范围',
  `remark` text NOT NULL COMMENT '备注',
  PRIMARY KEY (`id`),
  KEY `company_id` (`company_id`),
  KEY `create_at` (`create_at`),
  FULLTEXT KEY `openid` (`openid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=46 ;

-- --------------------------------------------------------

--
-- 表的结构 `CurrentLocation`
--

DROP TABLE IF EXISTS `CurrentLocation`;
CREATE TABLE IF NOT EXISTS `CurrentLocation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `baiduLat` double NOT NULL DEFAULT '0',
  `baiduLng` double NOT NULL DEFAULT '0',
  `qqLat` double NOT NULL DEFAULT '0',
  `qqLng` double NOT NULL DEFAULT '0',
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT '0' COMMENT '海拔',
  `battery` int(11) NOT NULL DEFAULT '0' COMMENT '电池电量百分比',
  `gsm_intensity` int(11) DEFAULT NULL COMMENT 'GSM信号强度',
  `seatStatus` text COMMENT '记录座位在位信息状态',
  `seated_num` int(11) NOT NULL DEFAULT '0' COMMENT '在位人数',
  `gpsLocalTime` datetime NOT NULL COMMENT '依据时区、GPS标准时间，对上报时间进行修正',
  `history_id` int(11) NOT NULL,
  `moveSpeaker` text NOT NULL COMMENT '移位喇叭响',
  `powerOffSpeaker` text NOT NULL COMMENT '断电喇叭响',
  `lock_error` int(11) NOT NULL DEFAULT '0' COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL DEFAULT '0' COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL DEFAULT '0' COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL DEFAULT '0' COMMENT '总线故障',
  `acc_state` int(11) NOT NULL DEFAULT '0' COMMENT 'acc 开',
  `loaded` int(11) NOT NULL DEFAULT '0' COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL DEFAULT '0' COMMENT '车门开',
  `secrity` int(11) NOT NULL DEFAULT '0' COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL DEFAULT '0' COMMENT '设防状态',
  `long_light` int(11) NOT NULL DEFAULT '0' COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL DEFAULT '0' COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL DEFAULT '0' COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL DEFAULT '0' COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL DEFAULT '0' COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL DEFAULT '0' COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL DEFAULT '0' COMMENT '车门开',
  `short_light` int(11) NOT NULL DEFAULT '0' COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL DEFAULT '0' COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL DEFAULT '0' COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL DEFAULT '0' COMMENT '盗警',
  `alm_sos` int(11) NOT NULL DEFAULT '0' COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL DEFAULT '0' COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL DEFAULT '0' COMMENT '超速报警',
  `alm_out` int(11) NOT NULL DEFAULT '0' COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL DEFAULT '0' COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL DEFAULT '0' COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL DEFAULT '0' COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL DEFAULT '0' COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL DEFAULT '0' COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL DEFAULT '0' COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL DEFAULT '0' COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL DEFAULT '0' COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL DEFAULT '0' COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL DEFAULT '0' COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL DEFAULT '0' COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL DEFAULT '0' COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL DEFAULT '0' COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC,',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `data_report_at` datetime DEFAULT NULL COMMENT '数据通道上报时间',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`),
  KEY `gpsTime` (`gpsTime`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=477 ;

-- --------------------------------------------------------

--
-- 表的结构 `Customer`
--

DROP TABLE IF EXISTS `Customer`;
CREATE TABLE IF NOT EXISTS `Customer` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openid` text NOT NULL,
  `gpsLat` float DEFAULT NULL,
  `gpsLng` float DEFAULT NULL,
  `upload_time` datetime DEFAULT NULL,
  `weixin` text,
  `phone` text,
  `address` text,
  `city` text,
  `nickname` text,
  `subscribe_at` datetime NOT NULL,
  `unsubscribe_at` datetime DEFAULT NULL,
  `province` text NOT NULL,
  `country` text NOT NULL,
  `weixinname` text NOT NULL COMMENT '微信名称',
  `qq` text NOT NULL,
  `baiduLat` float DEFAULT NULL,
  `baiduLng` float DEFAULT NULL,
  `qqLat` float DEFAULT NULL,
  `qqLng` float DEFAULT NULL,
  `dialogue_imei` text COMMENT '对话窗口的设备，用于智能手表',
  `dialogue_time` datetime DEFAULT NULL COMMENT '通话的最后时间',
  `last_imei` text NOT NULL COMMENT '最近浏览的可对话的设备',
  `last_imei_time` datetime DEFAULT NULL COMMENT '浏览时间',
  `headimgurl` text COMMENT '头像链接',
  `groupid` int(11) NOT NULL DEFAULT '0',
  `seat_type` text COMMENT '大巴车座位类型：seat,bed',
  `unionid` text NOT NULL COMMENT '微信unionid',
  `webopenid` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`),
  KEY `upload_time` (`upload_time`),
  KEY `subscribe_at` (`subscribe_at`),
  KEY `unsubscribe_at` (`unsubscribe_at`),
  KEY `last_imei_time` (`last_imei_time`),
  KEY `dialogue_time` (`dialogue_time`),
  FULLTEXT KEY `openid` (`openid`),
  FULLTEXT KEY `unionid` (`unionid`),
  FULLTEXT KEY `webopenid` (`webopenid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=548 ;

-- --------------------------------------------------------

--
-- 表的结构 `CustomerSeat`
--

DROP TABLE IF EXISTS `CustomerSeat`;
CREATE TABLE IF NOT EXISTS `CustomerSeat` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `seatstatus` text NOT NULL,
  `update_at` datetime DEFAULT NULL,
  `seated_percent` int(11) NOT NULL DEFAULT '50' COMMENT '有人的状态占总数的比重，判定为有人',
  `seated_interval` int(11) NOT NULL DEFAULT '5' COMMENT '统计时间段，从现在往前多少分钟',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=37 ;

-- --------------------------------------------------------

--
-- 表的结构 `Device`
--

DROP TABLE IF EXISTS `Device`;
CREATE TABLE IF NOT EXISTS `Device` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `devType` text NOT NULL,
  `timeZone` int(11) DEFAULT NULL,
  `subZone` int(11) DEFAULT NULL,
  `timeDir` text,
  `lang` text,
  `heardbeat_at` datetime NOT NULL COMMENT '记录最近的心跳时间',
  `name` text,
  `seat_status` text NOT NULL COMMENT '设备所属分组，每个设备必定要属于一个组',
  `Distributor_id` int(11) NOT NULL DEFAULT '1' COMMENT '分销商id',
  `phone` text COMMENT '设备绑定的手机号码',
  `expired_at` date DEFAULT NULL COMMENT '平台服务到期日期',
  `regedit_at` datetime DEFAULT NULL COMMENT '设备注册时间',
  `manufacturer` text NOT NULL COMMENT '硬件制造厂商',
  `service_start` date DEFAULT NULL COMMENT '服务开始日期',
  `mileage_id` int(11) DEFAULT NULL,
  `saled_at` datetime DEFAULT NULL,
  `warehouse_id` int(11) NOT NULL DEFAULT '1' COMMENT '进货的分销商',
  `stopTime` datetime DEFAULT NULL COMMENT '停止时间',
  `stopBaiduLat` double DEFAULT NULL,
  `stopBaiduLng` double DEFAULT NULL,
  `fireMinutes` int(11) DEFAULT NULL COMMENT '静止后，多少分钟后自动设防',
  `fireDistance` int(11) DEFAULT NULL COMMENT '离开多少米后，促发报警',
  `fireSpeaker` int(11) DEFAULT NULL,
  `monitorState` text COMMENT '检测状态:on-出现情况，启动监控，waiting-等待启动监控条件，fired-解除监控;alarm-报警正在促发',
  `lost_alm_after_minutes` int(11) DEFAULT NULL COMMENT '失联后多少分钟启动报警',
  `moveSpeaker` text COMMENT '移位鸣喇叭',
  `poweroffSpeaker` text COMMENT '正常电源断鸣喇叭',
  `monitor_at` datetime DEFAULT NULL COMMENT '启动设防时间',
  `ver` text COMMENT 'gps软件版本',
  `domain` text COMMENT '域名',
  `ip` text COMMENT 'ip地址',
  `port` text COMMENT '上报端口',
  `apn` text COMMENT '移动APN',
  `sos` text COMMENT '主监控号',
  `report_duration` int(11) DEFAULT NULL COMMENT 'gps上报间隔，单位 秒',
  `eavesdrop_switch` text COMMENT '监听开关,on/off',
  `sms_switch` text COMMENT '短信开关，on',
  `lost_state` text COMMENT '失联状态：short-7天内，15分钟以上;long-7天以上，该标识会被心跳自动清除',
  `arm_type` text COMMENT '检测目标类型：motor-摩托车；car-小车；bus-大巴车；old-man-老人；child-小孩',
  `report_needed` int(11) DEFAULT NULL COMMENT '是否需要上报，1-需要;其他不需要',
  `seat_type` text COMMENT '座位类型，seat，bed,midbus',
  `seat_template` text,
  `demo` int(11) DEFAULT NULL COMMENT '是否为demo标志',
  `sensor_id` int(11) NOT NULL DEFAULT '1' COMMENT '传感器类型id',
  `threads` text COMMENT '进程标志号:site_analyze-',
  `box_url` text,
  `box_cmd` text COMMENT 'busbox的指令',
  `cmd_ret` text COMMENT 'busbox执行后的返回结果，在下次之前会被清除',
  PRIMARY KEY (`id`),
  KEY `dev_imei` (`imei`(20)),
  KEY `subZone` (`subZone`),
  KEY `expired_at` (`expired_at`),
  KEY `sensor_id` (`sensor_id`),
  KEY `demo` (`demo`),
  KEY `Distributor_id` (`Distributor_id`,`expired_at`,`regedit_at`,`warehouse_id`,`stopTime`,`monitor_at`,`sensor_id`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `threads` (`threads`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=308 ;

-- --------------------------------------------------------

--
-- 表的结构 `DeviceGroup`
--

DROP TABLE IF EXISTS `DeviceGroup`;
CREATE TABLE IF NOT EXISTS `DeviceGroup` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `Customer_openid` text NOT NULL,
  `name` text NOT NULL,
  `description` text NOT NULL,
  `type` text NOT NULL COMMENT '分组类型，当前只有共享视图/自定义管理两种',
  `created_at` datetime NOT NULL,
  `belong_to` text NOT NULL COMMENT '取值：company-车队 person-个人',
  PRIMARY KEY (`id`),
  KEY `created_at` (`created_at`),
  FULLTEXT KEY `Customer_openid` (`Customer_openid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=40 ;

-- --------------------------------------------------------

--
-- 表的结构 `Distributor`
--

DROP TABLE IF EXISTS `Distributor`;
CREATE TABLE IF NOT EXISTS `Distributor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text COMMENT '真实姓名',
  `idCard` text,
  `idAddr` text COMMENT '身份证地址',
  `workAddr` text COMMENT '工作地点',
  `account` int(11) DEFAULT NULL COMMENT '销售收入',
  `weixin` text,
  `qq` int(11) DEFAULT NULL,
  `phone` text COMMENT '联系手机号码',
  `weixinpay_account` text COMMENT '微信支付账号',
  `alipay` text COMMENT '支付宝支付账号',
  `updstributor_id` int(11) DEFAULT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL,
  `WeixinQRcodeScene_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `valid` text NOT NULL COMMENT '是否有效：有效/失效',
  `confirmed_at` datetime NOT NULL COMMENT '用户确认的日期，也就是授权成功的日期',
  `Customer_openid` text NOT NULL,
  `company` text NOT NULL,
  `country` text COMMENT '国别',
  PRIMARY KEY (`id`),
  KEY `updstributor_id` (`updstributor_id`,`created_at`,`confirmed_at`),
  FULLTEXT KEY `idCard` (`idCard`),
  FULLTEXT KEY `province` (`province`),
  FULLTEXT KEY `Customer_openid` (`Customer_openid`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=15 ;

-- --------------------------------------------------------

--
-- 表的结构 `GlobalDefines`
--

DROP TABLE IF EXISTS `GlobalDefines`;
CREATE TABLE IF NOT EXISTS `GlobalDefines` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL COMMENT '变量的名称',
  `value` int(11) NOT NULL COMMENT '取值',
  `context` text NOT NULL COMMENT '内容描述',
  `f1` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `id` (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- 表的结构 `GlobalPara`
--

DROP TABLE IF EXISTS `GlobalPara`;
CREATE TABLE IF NOT EXISTS `GlobalPara` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` text NOT NULL,
  `value` text NOT NULL,
  `create_at` datetime NOT NULL,
  `expired_at` int(11) DEFAULT '0',
  `owner` text NOT NULL,
  `used_num` int(11) NOT NULL DEFAULT '0' COMMENT '程序调用次数',
  `value1` int(11) NOT NULL DEFAULT '0' COMMENT '服务价格',
  PRIMARY KEY (`id`),
  KEY `create_at` (`create_at`),
  KEY `expired_at` (`expired_at`),
  FULLTEXT KEY `name` (`name`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7507 ;

-- --------------------------------------------------------

--
-- 表的结构 `GroupHasDevice`
--

DROP TABLE IF EXISTS `GroupHasDevice`;
CREATE TABLE IF NOT EXISTS `GroupHasDevice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `devicegroup_id` int(11) NOT NULL,
  `created_at` datetime NOT NULL,
  `privilege` text NOT NULL COMMENT '权限，invisible-不可见 visible-可见',
  `no_help_theft` int(11) NOT NULL COMMENT '帮助朋友防贼，0-帮助防贼，1-放弃帮助',
  PRIMARY KEY (`id`),
  KEY `devicegroup_id` (`devicegroup_id`,`created_at`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=205 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack`
--

DROP TABLE IF EXISTS `HistoryTrack`;
CREATE TABLE IF NOT EXISTS `HistoryTrack` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL DEFAULT '0',
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL DEFAULT '0',
  `qqLng` double NOT NULL DEFAULT '0',
  `baiduLat` double NOT NULL DEFAULT '0',
  `baiduLng` double NOT NULL DEFAULT '0',
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) DEFAULT '0' COMMENT '电池电量百分比',
  `gsm_intensity` int(11) DEFAULT '0' COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float DEFAULT '0',
  `gmileage` float DEFAULT '0' COMMENT '几何公里数',
  `lock_error` int(11) DEFAULT '0' COMMENT '锁车电路故障',
  `gps_error` int(11) DEFAULT '0' COMMENT 'gps模块故障',
  `gsm_error` int(11) DEFAULT '0' COMMENT 'gsm模块故障',
  `bus_error` int(11) DEFAULT '0' COMMENT '总线故障',
  `acc_state` int(11) DEFAULT '0' COMMENT 'acc 开',
  `loaded` int(11) DEFAULT '0' COMMENT '重车（载客）',
  `door_opened` int(11) DEFAULT '0' COMMENT '车门开',
  `secrity` int(11) DEFAULT '0' COMMENT '私密状态',
  `gps_radio` text COMMENT '天线状态',
  `sf` int(11) DEFAULT '0' COMMENT '设防状态',
  `long_light` int(11) DEFAULT '0' COMMENT '远灯亮',
  `right_turn_light` int(11) DEFAULT '0' COMMENT '右转向灯亮',
  `left_turn_light` int(11) DEFAULT '0' COMMENT '左转向灯亮',
  `brake_light` int(11) DEFAULT '0' COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) DEFAULT '0' COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) DEFAULT '0' COMMENT '前雾灯亮',
  `door_closed` int(11) DEFAULT '0' COMMENT '车门开',
  `short_light` int(11) DEFAULT '0' COMMENT '近灯亮',
  `alm_crash` int(11) DEFAULT '0' COMMENT '碰撞报警',
  `alm_shake` int(11) DEFAULT '0' COMMENT '震动报警',
  `alm_theft` int(11) DEFAULT '0' COMMENT '盗警',
  `alm_sos` int(11) DEFAULT '0' COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) DEFAULT '0' COMMENT '：偏离路线报警',
  `alm_speed` int(11) DEFAULT '0' COMMENT '超速报警',
  `alm_out` int(11) DEFAULT '0' COMMENT '出范围报警',
  `alm_in` int(11) DEFAULT '0' COMMENT '进范围报警',
  `alm_invalid_opened` int(11) DEFAULT '0' COMMENT '非法开车门',
  `alm_invalid_moved` int(11) DEFAULT '0' COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL DEFAULT '0' COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL DEFAULT '0' COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) DEFAULT '0' COMMENT '推车报警',
  `alm_low_voltage` int(11) DEFAULT '0' COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) DEFAULT '0' COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) DEFAULT '0' COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) DEFAULT '0' COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) DEFAULT '0' COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) DEFAULT '0' COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) DEFAULT '0' COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  `seated_num` int(11) DEFAULT NULL,
  `img_path` text COMMENT '图片存储位置',
  `video_path` text COMMENT '视频存储位置',
  PRIMARY KEY (`id`),
  KEY `gpsTime` (`gpsTime`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1258677 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack1`
--

DROP TABLE IF EXISTS `HistoryTrack1`;
CREATE TABLE IF NOT EXISTS `HistoryTrack1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `image_path` text NOT NULL COMMENT '图片文件地址',
  `video_path` text NOT NULL COMMENT '录像文件地址',
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT '0',
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL DEFAULT '0',
  `qqLng` double NOT NULL DEFAULT '0',
  `baiduLat` double NOT NULL DEFAULT '0',
  `baiduLng` double NOT NULL DEFAULT '0',
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT '0' COMMENT '海拔',
  `battery` int(11) NOT NULL DEFAULT '0' COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL DEFAULT '0' COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seated_num` int(11) NOT NULL DEFAULT '0' COMMENT '在位人数据',
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL DEFAULT '0',
  `gmileage` float DEFAULT '0' COMMENT '几何距离',
  `lock_error` int(11) NOT NULL DEFAULT '0' COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL DEFAULT '0' COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL DEFAULT '0' COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL DEFAULT '0' COMMENT '总线故障',
  `acc_state` int(11) NOT NULL DEFAULT '0' COMMENT 'acc 开',
  `loaded` int(11) NOT NULL DEFAULT '0' COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL DEFAULT '0' COMMENT '车门开',
  `secrity` int(11) NOT NULL DEFAULT '0' COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL DEFAULT '0' COMMENT '设防状态',
  `long_light` int(11) NOT NULL DEFAULT '0' COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL DEFAULT '0' COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL DEFAULT '0' COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL DEFAULT '0' COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL DEFAULT '0' COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL DEFAULT '0' COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL DEFAULT '0' COMMENT '车门开',
  `short_light` int(11) NOT NULL DEFAULT '0' COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL DEFAULT '0' COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL DEFAULT '0' COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL DEFAULT '0' COMMENT '盗警',
  `alm_sos` int(11) NOT NULL DEFAULT '0' COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL DEFAULT '0' COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL DEFAULT '0' COMMENT '超速报警',
  `alm_out` int(11) NOT NULL DEFAULT '0' COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL DEFAULT '0' COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL DEFAULT '0' COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL DEFAULT '0' COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL DEFAULT '0' COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL DEFAULT '0' COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL DEFAULT '0' COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL DEFAULT '0' COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL DEFAULT '0' COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL DEFAULT '0' COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL DEFAULT '0' COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL DEFAULT '0' COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL DEFAULT '0' COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL DEFAULT '0' COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  `site_analyzed_flag` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `gpsTime` (`gpsTime`),
  KEY `report_at` (`report_at`),
  KEY `gmileage` (`gmileage`),
  KEY `gpsTime_2` (`gpsTime`,`gmileage`),
  KEY `report_at_3` (`report_at`,`gpsTime`,`gmileage`),
  KEY `gpsTime_3` (`gpsTime`,`site_analyzed_flag`),
  KEY `gpsTime_4` (`gpsTime`,`gmileage`,`site_analyzed_flag`),
  KEY `site_analyzed_flag` (`site_analyzed_flag`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6783830 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack2`
--

DROP TABLE IF EXISTS `HistoryTrack2`;
CREATE TABLE IF NOT EXISTS `HistoryTrack2` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack3`
--

DROP TABLE IF EXISTS `HistoryTrack3`;
CREATE TABLE IF NOT EXISTS `HistoryTrack3` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack4`
--

DROP TABLE IF EXISTS `HistoryTrack4`;
CREATE TABLE IF NOT EXISTS `HistoryTrack4` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack5`
--

DROP TABLE IF EXISTS `HistoryTrack5`;
CREATE TABLE IF NOT EXISTS `HistoryTrack5` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack6`
--

DROP TABLE IF EXISTS `HistoryTrack6`;
CREATE TABLE IF NOT EXISTS `HistoryTrack6` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack7`
--

DROP TABLE IF EXISTS `HistoryTrack7`;
CREATE TABLE IF NOT EXISTS `HistoryTrack7` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack8`
--

DROP TABLE IF EXISTS `HistoryTrack8`;
CREATE TABLE IF NOT EXISTS `HistoryTrack8` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack9`
--

DROP TABLE IF EXISTS `HistoryTrack9`;
CREATE TABLE IF NOT EXISTS `HistoryTrack9` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack10`
--

DROP TABLE IF EXISTS `HistoryTrack10`;
CREATE TABLE IF NOT EXISTS `HistoryTrack10` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack11`
--

DROP TABLE IF EXISTS `HistoryTrack11`;
CREATE TABLE IF NOT EXISTS `HistoryTrack11` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack12`
--

DROP TABLE IF EXISTS `HistoryTrack12`;
CREATE TABLE IF NOT EXISTS `HistoryTrack12` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack13`
--

DROP TABLE IF EXISTS `HistoryTrack13`;
CREATE TABLE IF NOT EXISTS `HistoryTrack13` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack14`
--

DROP TABLE IF EXISTS `HistoryTrack14`;
CREATE TABLE IF NOT EXISTS `HistoryTrack14` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack15`
--

DROP TABLE IF EXISTS `HistoryTrack15`;
CREATE TABLE IF NOT EXISTS `HistoryTrack15` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrack16`
--

DROP TABLE IF EXISTS `HistoryTrack16`;
CREATE TABLE IF NOT EXISTS `HistoryTrack16` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `report_at` datetime NOT NULL,
  `gpsLat` double NOT NULL,
  `gpsLng` double NOT NULL,
  `speed` float NOT NULL,
  `realState` text,
  `lngType` text,
  `latType` text,
  `direction` int(11) DEFAULT NULL,
  `addr` text NOT NULL,
  `province` text NOT NULL,
  `city` text NOT NULL,
  `district` text NOT NULL COMMENT '区县',
  `gpsReport` text,
  `reportMode` text,
  `ACC` int(11) DEFAULT NULL,
  `CellID` int(11) DEFAULT NULL,
  `LAC` int(11) DEFAULT NULL,
  `MNC` int(11) DEFAULT NULL,
  `MCC` int(11) DEFAULT NULL,
  `satNum` int(11) DEFAULT NULL,
  `locatedState` text,
  `gpsTime` datetime DEFAULT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `country` text NOT NULL,
  `alarm` text COMMENT '报警信息',
  `height` int(11) DEFAULT NULL COMMENT '海拔',
  `battery` int(11) NOT NULL COMMENT '电池电量百分比',
  `gsm_intensity` int(11) NOT NULL COMMENT 'GSM信号强度',
  `seatStatus` text,
  `seatStatus2` text NOT NULL COMMENT '矫正的座位状态信息',
  `mileage` float NOT NULL,
  `gmileage` float NOT NULL COMMENT '几何公里数',
  `lock_error` int(11) NOT NULL COMMENT '锁车电路故障',
  `gps_error` int(11) NOT NULL COMMENT 'gps模块故障',
  `gsm_error` int(11) NOT NULL COMMENT 'gsm模块故障',
  `bus_error` int(11) NOT NULL COMMENT '总线故障',
  `acc_state` int(11) NOT NULL COMMENT 'acc 开',
  `loaded` int(11) NOT NULL COMMENT '重车（载客）',
  `door_opened` int(11) NOT NULL COMMENT '车门开',
  `secrity` int(11) NOT NULL COMMENT '私密状态',
  `gps_radio` text NOT NULL COMMENT '天线状态',
  `sf` int(11) NOT NULL COMMENT '设防状态',
  `long_light` int(11) NOT NULL COMMENT '远灯亮',
  `right_turn_light` int(11) NOT NULL COMMENT '右转向灯亮',
  `left_turn_light` int(11) NOT NULL COMMENT '左转向灯亮',
  `brake_light` int(11) NOT NULL COMMENT '刹车灯亮',
  `backLight_backFogLamp_speaker` int(11) NOT NULL COMMENT '倒车灯开or后雾灯开or喇叭鸣',
  `front_fog_lamp` int(11) NOT NULL COMMENT '前雾灯亮',
  `door_closed` int(11) NOT NULL COMMENT '车门开',
  `short_light` int(11) NOT NULL COMMENT '近灯亮',
  `alm_crash` int(11) NOT NULL COMMENT '碰撞报警',
  `alm_shake` int(11) NOT NULL COMMENT '震动报警',
  `alm_theft` int(11) NOT NULL COMMENT '盗警',
  `alm_sos` int(11) NOT NULL COMMENT '紧急报警/SOS/劫警',
  `alm_road` int(11) NOT NULL COMMENT '：偏离路线报警',
  `alm_speed` int(11) NOT NULL COMMENT '超速报警',
  `alm_out` int(11) NOT NULL COMMENT '出范围报警',
  `alm_in` int(11) NOT NULL COMMENT '进范围报警',
  `alm_invalid_opened` int(11) NOT NULL COMMENT '非法开车门',
  `alm_invalid_moved` int(11) NOT NULL COMMENT '位移报警/非法移动报警/越站报警',
  `alm_short_stop_time` int(11) NOT NULL COMMENT '停车休息时间不足报警',
  `alm_invalid_time` int(11) NOT NULL COMMENT '：非法时段行驶报警',
  `alm_pushed` int(11) NOT NULL COMMENT '推车报警',
  `alm_low_voltage` int(11) NOT NULL COMMENT '电瓶电压低报警',
  `alm_power_off` int(11) NOT NULL COMMENT '断电报警/剪线报警',
  `alm_sercity_lock` int(11) NOT NULL COMMENT '暗锁报警',
  `alm_coolant_high_temperature` int(11) NOT NULL COMMENT '冷却液温度过高报警（OBD）',
  `alm_deceleration` int(11) NOT NULL COMMENT '：急减速报警（OBD）',
  `alm_acceleration` int(11) NOT NULL COMMENT '：急加速报警（OBD）',
  `alm_stop_fireon` int(11) NOT NULL COMMENT '：停车未熄火报警/禁行报警',
  `lbs_cell` text COMMENT '基站定位信息num,MCC,MNC',
  `lbs_wifi` text COMMENT 'wifi定位信息num,wifi_name,mac,sign',
  `local_addr` text COMMENT '本地化地名',
  `distance` int(11) DEFAULT NULL COMMENT 'local_addr精度',
  PRIMARY KEY (`id`),
  KEY `report_at` (`report_at`,`gpsTime`),
  FULLTEXT KEY `imei` (`imei`),
  FULLTEXT KEY `imei_2` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `HistoryTrackTable`
--

DROP TABLE IF EXISTS `HistoryTrackTable`;
CREATE TABLE IF NOT EXISTS `HistoryTrackTable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tableName` text NOT NULL,
  `from_time` datetime NOT NULL,
  `to_time` datetime NOT NULL,
  `created_at` datetime NOT NULL,
  `sum` int(11) NOT NULL,
  `max_sum` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`,`to_time`,`created_at`,`max_sum`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=17 ;

-- --------------------------------------------------------

--
-- 表的结构 `LinePrice`
--

DROP TABLE IF EXISTS `LinePrice`;
CREATE TABLE IF NOT EXISTS `LinePrice` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_site_id` int(11) NOT NULL COMMENT '上车站点',
  `to_site_id` int(11) NOT NULL COMMENT '到站站点',
  `price` int(11) NOT NULL COMMENT '价格',
  `BusLine_id` int(11) NOT NULL COMMENT '所属班车线路',
  PRIMARY KEY (`id`),
  KEY `from_site_id` (`from_site_id`,`to_site_id`,`BusLine_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=173 ;

-- --------------------------------------------------------

--
-- 表的结构 `LineSites`
--

DROP TABLE IF EXISTS `LineSites`;
CREATE TABLE IF NOT EXISTS `LineSites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `busline_id` int(11) NOT NULL COMMENT '线路id',
  `site_id` int(11) NOT NULL COMMENT '站点id',
  `seq` int(11) NOT NULL COMMENT '序号',
  `is_end` text COMMENT '是否为终点站:yes',
  PRIMARY KEY (`id`),
  KEY `seq` (`seq`),
  KEY `busline_id` (`busline_id`,`site_id`,`seq`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 COMMENT='线路的站点表' AUTO_INCREMENT=2559 ;

-- --------------------------------------------------------

--
-- 表的结构 `Manager`
--

DROP TABLE IF EXISTS `Manager`;
CREATE TABLE IF NOT EXISTS `Manager` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `openid` text NOT NULL,
  `range` text NOT NULL,
  `weixinname` text NOT NULL,
  `privilege` text NOT NULL,
  `name` text NOT NULL,
  `report` text NOT NULL,
  `enRange` text NOT NULL,
  `remark` text NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=35 ;

-- --------------------------------------------------------

--
-- 表的结构 `MonitorRegion`
--

DROP TABLE IF EXISTS `MonitorRegion`;
CREATE TABLE IF NOT EXISTS `MonitorRegion` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `from_site_id` int(11) NOT NULL COMMENT '截止位置',
  `to_site_id` int(11) NOT NULL COMMENT '开始位置',
  `gmileage` int(11) NOT NULL COMMENT '距离里程',
  `speed` int(11) NOT NULL COMMENT '平均速度',
  `busline_id` int(11) NOT NULL COMMENT '关联线路',
  `receiver` text NOT NULL COMMENT '接收类型：customer-直接发给用户，-manager-管理者审核',
  `direction` int(11) NOT NULL DEFAULT '0' COMMENT '车辆行驶方向',
  `times_percent` int(11) NOT NULL DEFAULT '50' COMMENT '有人次数占比，则认为有人',
  `mileage_percent` int(11) NOT NULL DEFAULT '50' COMMENT '有人里程数占比，则认为有人',
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=37 ;

-- --------------------------------------------------------

--
-- 表的结构 `MonitorResult`
--

DROP TABLE IF EXISTS `MonitorResult`;
CREATE TABLE IF NOT EXISTS `MonitorResult` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `monitor_region_id` int(11) NOT NULL,
  `from_history_track_id` int(11) NOT NULL DEFAULT '-1' COMMENT '监控的运行位置id',
  `to_history_track_id` int(11) NOT NULL DEFAULT '-1' COMMENT '监控的运行位置id',
  `seatStatus` text COMMENT '空座数',
  `imei` text NOT NULL,
  `from_time` datetime DEFAULT NULL,
  `to_time` datetime DEFAULT NULL,
  `checked_his_id` int(11) NOT NULL DEFAULT '0' COMMENT '记录上次检查到的historytrack_id',
  `create_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `time_sum` int(11) NOT NULL DEFAULT '0' COMMENT '按次数统计的人数',
  `mileage_sum` int(11) DEFAULT '0' COMMENT '按里程统计的人数',
  `speed` int(11) NOT NULL DEFAULT '0' COMMENT '平均车速',
  `duration_time` text NOT NULL COMMENT '耗时',
  `duration_mileage` int(11) NOT NULL DEFAULT '0' COMMENT '行程（公里）',
  `checked_sum` int(11) NOT NULL DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`,`to_time`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=6243 ;

-- --------------------------------------------------------

--
-- 表的结构 `QrsceneAllocation`
--

DROP TABLE IF EXISTS `QrsceneAllocation`;
CREATE TABLE IF NOT EXISTS `QrsceneAllocation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tableName` text NOT NULL COMMENT '微信二维码应用的数据库表',
  `start_scene` int(11) NOT NULL COMMENT '分配的开始id',
  `end_scene` int(11) NOT NULL COMMENT '分配的结束id',
  PRIMARY KEY (`id`),
  KEY `start_scene` (`start_scene`,`end_scene`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=2 ;

-- --------------------------------------------------------

--
-- 表的结构 `SeatStatus`
--

DROP TABLE IF EXISTS `SeatStatus`;
CREATE TABLE IF NOT EXISTS `SeatStatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `sensor_no` int(11) NOT NULL,
  `seat_state` text NOT NULL,
  `bustravel_id` int(11) NOT NULL DEFAULT '0' COMMENT '0:处于初始化态的 -1:该节点被分割，-2：没有被分配到行程的孤儿',
  `from_speed` float NOT NULL DEFAULT '-1',
  `to_speed` float NOT NULL DEFAULT '-1',
  `from_time` datetime DEFAULT NULL,
  `to_time` datetime DEFAULT NULL,
  `duration_seconds` int(11) NOT NULL DEFAULT '-1' COMMENT '持续时间，单位秒',
  `duration_gmileage` float NOT NULL DEFAULT '-1' COMMENT '停车期间移动的距离，单位：公里',
  `to_gmileage` float NOT NULL DEFAULT '-1' COMMENT '出站的公里标签',
  `from_gmileage` float NOT NULL DEFAULT '-1' COMMENT '进站的公里标签',
  `to_historytrack_id` int(11) NOT NULL DEFAULT '-1' COMMENT '历史记录索引',
  `from_historytrack_id` int(11) NOT NULL COMMENT '历史记录索引',
  `dithering_id` int(11) DEFAULT '-1' COMMENT '抖动合并后的id',
  `from_travel_site_id` int(11) DEFAULT '0' COMMENT '开始站点',
  `to_travel_site_id` int(11) DEFAULT '0' COMMENT '截止站点',
  `sites_gmileage` float NOT NULL DEFAULT '0' COMMENT '设计站点间的里程',
  `gmileage_travel_percent` float NOT NULL DEFAULT '0' COMMENT '在位里程/站点间里程',
  `gmileage_sites_percent` float NOT NULL DEFAULT '0' COMMENT '在位里程/总里程',
  `parent_id` int(11) NOT NULL DEFAULT '0' COMMENT '父节点，缺省是0，表明该节点没有被分割',
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`),
  KEY `to_time` (`to_time`),
  KEY `bustravel_id` (`bustravel_id`),
  KEY `sensor_no` (`sensor_no`),
  KEY `sensor_no_2` (`sensor_no`,`from_time`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=32484078 ;

-- --------------------------------------------------------

--
-- 表的结构 `SeatStatusDithering`
--

DROP TABLE IF EXISTS `SeatStatusDithering`;
CREATE TABLE IF NOT EXISTS `SeatStatusDithering` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `sensor_no` int(11) NOT NULL,
  `seat_state` text NOT NULL,
  `bustravel_id` int(11) NOT NULL DEFAULT '0',
  `from_speed` float NOT NULL DEFAULT '-1',
  `to_speed` float NOT NULL DEFAULT '-1',
  `from_time` datetime DEFAULT NULL,
  `to_time` datetime DEFAULT NULL,
  `duration_seconds` int(11) NOT NULL DEFAULT '-1' COMMENT '持续时间，单位秒',
  `duration_gmileage` float NOT NULL DEFAULT '-1' COMMENT '停车期间移动的距离，单位：公里',
  `to_gmileage` float NOT NULL DEFAULT '-1' COMMENT '出站的公里标签',
  `from_gmileage` float NOT NULL DEFAULT '-1' COMMENT '进站的公里标签',
  `to_historytrack_id` int(11) NOT NULL DEFAULT '-1' COMMENT '历史记录索引',
  `from_historytrack_id` int(11) NOT NULL COMMENT '历史记录索引',
  `dithering_id` int(11) DEFAULT NULL COMMENT '抖动合并后的id',
  `from_manual_site_id` int(11) DEFAULT NULL COMMENT '开始站点',
  `to_manual_site_id` int(11) DEFAULT NULL COMMENT '截止站点',
  `sites_gmileage` float NOT NULL DEFAULT '0' COMMENT '设计站点间的里程',
  `dithering_num` int(11) NOT NULL DEFAULT '0' COMMENT '抖动次数',
  `gmileage_sites_percent` float NOT NULL DEFAULT '0' COMMENT '在当前设计站点间的比例',
  `gmileage_travel_percent` float NOT NULL DEFAULT '0' COMMENT '行程距离，在全程的比例',
  `dither_km` int(11) NOT NULL DEFAULT '0' COMMENT '在位里程/抖动次数',
  `seated_vote` text NOT NULL COMMENT '座位有效性判定结论',
  `seat_state_ch` text NOT NULL COMMENT '在位状态中文名字：空座，有人,超时,未知',
  `price` int(11) NOT NULL COMMENT '价格',
  `from_travel_site_id` int(11) NOT NULL DEFAULT '0' COMMENT '起始站点id',
  `to_travel_site_id` int(11) NOT NULL DEFAULT '0' COMMENT '终点站点id',
  PRIMARY KEY (`id`),
  KEY `sensor_no` (`sensor_no`),
  KEY `from_time` (`from_time`),
  KEY `to_time` (`to_time`),
  KEY `sensor_no_2` (`sensor_no`,`from_time`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=7959 ;

-- --------------------------------------------------------

--
-- 表的结构 `SeatStatusExchange`
--

DROP TABLE IF EXISTS `SeatStatusExchange`;
CREATE TABLE IF NOT EXISTS `SeatStatusExchange` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `sensor_no` int(11) NOT NULL,
  `seat_state` text NOT NULL,
  `bustravel_id` int(11) NOT NULL DEFAULT '0',
  `from_speed` float NOT NULL DEFAULT '-1',
  `to_speed` float NOT NULL DEFAULT '-1',
  `from_time` datetime DEFAULT NULL,
  `to_time` datetime DEFAULT NULL,
  `duration_seconds` int(11) NOT NULL DEFAULT '-1' COMMENT '持续时间，单位秒',
  `duration_gmileage` float NOT NULL DEFAULT '-1' COMMENT '停车期间移动的距离，单位：公里',
  `to_gmileage` float NOT NULL DEFAULT '-1' COMMENT '出站的公里标签',
  `from_gmileage` float NOT NULL DEFAULT '-1' COMMENT '进站的公里标签',
  `to_historytrack_id` int(11) NOT NULL DEFAULT '-1' COMMENT '历史记录索引',
  `from_historytrack_id` int(11) NOT NULL COMMENT '历史记录索引',
  `dithering_id` int(11) DEFAULT NULL COMMENT '抖动合并后的id',
  `from_manual_site_id` int(11) DEFAULT NULL COMMENT '开始站点',
  `to_manual_site_id` int(11) DEFAULT NULL COMMENT '截止站点',
  `sites_gmileage` float NOT NULL DEFAULT '0' COMMENT '设计站点间的里程',
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`),
  KEY `to_time` (`to_time`),
  KEY `sensor_no` (`sensor_no`,`from_time`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;

-- --------------------------------------------------------

--
-- 表的结构 `SeatType`
--

DROP TABLE IF EXISTS `SeatType`;
CREATE TABLE IF NOT EXISTS `SeatType` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `chName` text NOT NULL,
  `enName` text NOT NULL,
  `seat_num` int(11) NOT NULL DEFAULT '0',
  `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  FULLTEXT KEY `chName` (`chName`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=5 ;

-- --------------------------------------------------------

--
-- 表的结构 `Sensor`
--

DROP TABLE IF EXISTS `Sensor`;
CREATE TABLE IF NOT EXISTS `Sensor` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=4 ;

-- --------------------------------------------------------

--
-- 表的结构 `Sites`
--

DROP TABLE IF EXISTS `Sites`;
CREATE TABLE IF NOT EXISTS `Sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `setting_type` text COMMENT '站点设置方式：manul,auto',
  `gpsLat` double NOT NULL COMMENT '经度',
  `gpsLng` double NOT NULL COMMENT '纬度',
  `address` text NOT NULL COMMENT '具体位置',
  `name` text COMMENT '站点名称',
  `distance` int(11) DEFAULT NULL COMMENT '位置精度，单位米',
  `baiduLat` double NOT NULL,
  `baiduLng` double NOT NULL,
  `qqLat` double NOT NULL,
  `qqLng` double NOT NULL,
  `province` text,
  `city` text,
  `district` text,
  `site_type` text COMMENT '站点类型',
  `end_site` text COMMENT '是否为起始站点',
  PRIMARY KEY (`id`),
  FULLTEXT KEY `province` (`province`),
  FULLTEXT KEY `city` (`city`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1738 ;

-- --------------------------------------------------------

--
-- 表的结构 `SiteSeatStatus`
--

DROP TABLE IF EXISTS `SiteSeatStatus`;
CREATE TABLE IF NOT EXISTS `SiteSeatStatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `imei` text NOT NULL,
  `bustravel_id` int(11) NOT NULL DEFAULT '0',
  `busline_id` int(11) NOT NULL,
  `site_id` int(11) DEFAULT '0',
  `manual_site_id` int(11) NOT NULL,
  `from_speed` float NOT NULL DEFAULT '-1',
  `to_speed` float NOT NULL DEFAULT '-1',
  `from_time` datetime DEFAULT NULL,
  `to_time` datetime DEFAULT NULL,
  `num_change` int(11) NOT NULL DEFAULT '0' COMMENT '上下客变化数',
  `from_seated_num` int(11) NOT NULL DEFAULT '0',
  `to_seated_num` int(11) NOT NULL DEFAULT '0',
  `duration_seconds` int(11) NOT NULL COMMENT '持续时间，单位秒',
  `duration_gmileage` float NOT NULL COMMENT '停车期间移动的距离，单位：公里',
  `end_site_type` text NOT NULL COMMENT '是否为终点站：checking-检测中，traveling-等待确定起始点；start-开始站点，end：截止站点',
  `to_gmileage` float NOT NULL DEFAULT '-1' COMMENT '出站的公里标签',
  `from_gmileage` float NOT NULL DEFAULT '-1' COMMENT '进站的公里标签',
  `end_accuracy` float NOT NULL DEFAULT '0' COMMENT '终点偏差公里数',
  `to_historytrack_id` int(11) NOT NULL COMMENT '历史记录索引',
  `from_historytrack_id` int(11) NOT NULL COMMENT '历史记录索引',
  `site_accuracy` float DEFAULT NULL COMMENT '站点距离偏差',
  `site_type` text NOT NULL COMMENT '站点类型:manul--人工指定，random--随机停靠点',
  `end_accuracy_percent` float NOT NULL DEFAULT '-1',
  `site_accuracy_percent` float NOT NULL DEFAULT '-1',
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`),
  KEY `bustravel_id` (`bustravel_id`),
  KEY `to_time` (`to_time`),
  KEY `bustravel_id_2` (`from_time`,`to_time`,`to_gmileage`,`from_gmileage`),
  FULLTEXT KEY `imei` (`imei`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=1296037 ;

-- --------------------------------------------------------

--
-- 表的结构 `TradeOrder`
--

DROP TABLE IF EXISTS `TradeOrder`;
CREATE TABLE IF NOT EXISTS `TradeOrder` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `out_trade_no` text NOT NULL COMMENT '内部生成的交易单号',
  `openid` text NOT NULL COMMENT '订单的主人',
  `created_at` datetime NOT NULL COMMENT '订单产生时间',
  `type` text NOT NULL COMMENT '订单类型，目前有共享/转让两种订单',
  `trade` text NOT NULL COMMENT '订单内容，包括设备id，单价,总价',
  `weixin_trade_no` text COMMENT '微信支付订单号',
  `alipay_trade_no` text COMMENT '支付宝订单号',
  `total_fee` float DEFAULT NULL COMMENT '成交总价',
  `expired_at` datetime DEFAULT NULL COMMENT '过期时间',
  `weixinpay_state` text COMMENT '成交时间，或者是过期',
  `alipay_state` text COMMENT '成交时间，或者是过期',
  `qrcode_url` text NOT NULL,
  `share_url` text NOT NULL,
  `weixin_url` text NOT NULL,
  `state` text NOT NULL COMMENT '交易状态：close-已完成；其他-进行中',
  `owner` text,
  PRIMARY KEY (`id`),
  KEY `created_at` (`created_at`),
  KEY `expired_at` (`expired_at`),
  FULLTEXT KEY `openid` (`openid`),
  FULLTEXT KEY `out_trade_no` (`out_trade_no`),
  FULLTEXT KEY `owner` (`owner`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=52 ;

-- --------------------------------------------------------

--
-- 表的结构 `TravelSites`
--

DROP TABLE IF EXISTS `TravelSites`;
CREATE TABLE IF NOT EXISTS `TravelSites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `bustravel_id` int(11) NOT NULL,
  `site_seatstatus_id` int(11) NOT NULL,
  `site_type` text NOT NULL COMMENT 'pass:中间站，start:起点站，end:终点站',
  `from_time` datetime DEFAULT NULL COMMENT '停靠开始时间',
  `to_time` datetime DEFAULT NULL COMMENT '停靠截止时间',
  `manual_site_id` int(11) NOT NULL COMMENT '关联的设计站点id',
  `site_accuracy` float NOT NULL COMMENT '偏离最近的设计站点距离',
  `from_gmileage` float NOT NULL COMMENT '起始里程刻度',
  `to_gmileage` float NOT NULL COMMENT '出发时里程刻度',
  PRIMARY KEY (`id`),
  KEY `from_time` (`from_time`),
  KEY `to_time` (`to_time`),
  KEY `to_time_2` (`to_time`),
  KEY `from_time_2` (`from_time`),
  KEY `from_gmileage` (`from_gmileage`),
  KEY `to_gmileage` (`to_gmileage`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=20979 ;

-- --------------------------------------------------------

--
-- 表的结构 `UserAccess`
--

DROP TABLE IF EXISTS `UserAccess`;
CREATE TABLE IF NOT EXISTS `UserAccess` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `fullpath` text NOT NULL COMMENT '访问路径',
  `openid` text NOT NULL,
  `access_at` datetime NOT NULL COMMENT '访问时间',
  `domain` text NOT NULL COMMENT '域名',
  `access_date` date NOT NULL COMMENT '访问日期',
  `access_hour` int(11) NOT NULL COMMENT '访问时段',
  `pathinfo` text NOT NULL,
  `access_month` text NOT NULL COMMENT '月份',
  `access_week` date NOT NULL COMMENT '每周周末',
  `product` text NOT NULL,
  `weixin_orign_id` text,
  PRIMARY KEY (`id`),
  KEY `access_at` (`access_at`),
  KEY `access_date` (`access_date`),
  KEY `access_hour` (`access_hour`),
  KEY `access_week` (`access_week`)
) ENGINE=InnoDB  DEFAULT CHARSET=utf8 AUTO_INCREMENT=74761 ;

-- --------------------------------------------------------

--
-- 表的结构 `WeixinQRcodeScene`
--

DROP TABLE IF EXISTS `WeixinQRcodeScene`;
CREATE TABLE IF NOT EXISTS `WeixinQRcodeScene` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tableName` text NOT NULL COMMENT '微信二维码应用的数据库表',
  `table_id` int(11) NOT NULL COMMENT '微信二维码应用的数据库表的ID',
  `url` text NOT NULL,
  `qrcode_url` text NOT NULL,
  PRIMARY KEY (`id`),
  KEY `table_id` (`table_id`)
) ENGINE=MyISAM  DEFAULT CHARSET=utf8 AUTO_INCREMENT=9 ;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
