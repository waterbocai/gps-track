CREATE TRIGGER `BusTravel_After_Insert` AFTER INSERT ON `BusTravel`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) 
VALUES ('BusTravel','INSERT',NEW.id);

CREATE TRIGGER `BusTravel_After_DELETE` AFTER DELETE ON `BusTravel`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUEs ('BusTravel','DELETE',OLD.id);
 CREATE TRIGGER `BusTravel_After_Update` AFTER UPDATE ON `BusTravel`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('BusTravel','UPDATE',NEW.id);
 
 CREATE TRIGGER `LineSites_After_DELETE` AFTER DELETE ON `LineSites`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('LineSites','DELETE',OLD.id);
 CREATE TRIGGER `LineSites_After_Insert` AFTER INSERT ON `LineSites`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('LineSites','INSERT',NEW.id);
 CREATE TRIGGER `LineSites_After_Update` AFTER UPDATE ON `LineSites`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('LineSites','UPDATE',NEW.id);
 
 
 CREATE TRIGGER `SeatStatus_After_DELETE` AFTER DELETE ON `SeatStatus`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatus','DELETE',OLD.id);
 CREATE TRIGGER `SeatStatus_After_Insert` AFTER INSERT ON `SeatStatus`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatus','INSERT',NEW.id);
 CREATE TRIGGER `SeatStatus_After_Update` AFTER UPDATE ON `SeatStatus`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatus','UPDATE',NEW.id);
 
 
  CREATE TRIGGER `SeatStatusDithering_After_DELETE` AFTER DELETE ON `SeatStatusDithering`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatusDithering','DELETE',OLD.id);
 CREATE TRIGGER `SeatStatusDithering_After_Insert` AFTER INSERT ON `SeatStatusDithering`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatusDithering','INSERT',NEW.id);
 CREATE TRIGGER `SeatStatusDithering_After_Update` AFTER UPDATE ON `SeatStatusDithering`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatusDithering','UPDATE',NEW.id);
 
 
   CREATE TRIGGER `SeatStatusExchange_After_DELETE` AFTER DELETE ON `SeatStatusExchange`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatusExchange','DELETE',OLD.id);
 CREATE TRIGGER `SeatStatusExchange_After_Insert` AFTER INSERT ON `SeatStatusExchange`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatusExchange','INSERT',NEW.id);
 CREATE TRIGGER `SeatStatusExchange_After_Update` AFTER UPDATE ON `SeatStatusExchange`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SeatStatusExchange','UPDATE',NEW.id);
 
 
    CREATE TRIGGER `SiteSeatStatus_After_DELETE` AFTER DELETE ON `SiteSeatStatus`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SiteSeatStatus','DELETE',OLD.id);
 CREATE TRIGGER `SiteSeatStatus_After_Insert` AFTER INSERT ON `SiteSeatStatus`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SiteSeatStatus','INSERT',NEW.id);
 CREATE TRIGGER `SiteSeatStatus_After_Update` AFTER UPDATE ON `SiteSeatStatus`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('SiteSeatStatus','UPDATE',NEW.id);
 
 
     CREATE TRIGGER `TravelSites_After_DELETE` AFTER DELETE ON `TravelSites`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('TravelSites','DELETE',OLD.id);
 CREATE TRIGGER `TravelSites_After_Insert` AFTER INSERT ON `TravelSites`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('TravelSites','INSERT',NEW.id);
 CREATE TRIGGER `TravelSites_After_Update` AFTER UPDATE ON `TravelSites`
 FOR EACH ROW INSERT INTO  BakupChange (tableName,operate,table_id) VALUE ('TravelSites','UPDATE',NEW.id);
 