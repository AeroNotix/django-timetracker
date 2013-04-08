 ALTER TABLE `tracker_trackingentry` ADD `link_id` integer UNIQUE;
 ALTER TABLE `tracker_trackingentry` ADD CONSTRAINT `link_id_refs_id_28999898` FOREIGN KEY (`link_id`) REFERENCES `tracker_trackingentry` (`id`);
