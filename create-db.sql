-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema scene_search
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema scene_search
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `scene_search` DEFAULT CHARACTER SET utf8 ;
USE `scene_search` ;

-- -----------------------------------------------------
-- Table `scene_search`.`fine_class_stats`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`fine_class_stats` (
  `class` VARCHAR(30) NOT NULL DEFAULT '',
  `average` DECIMAL(5,2) UNSIGNED NOT NULL,
  `stddev` DECIMAL(5,2) UNSIGNED NOT NULL,
  `maximum` INT(11) UNSIGNED NOT NULL,
  `minimum` INT(11) UNSIGNED NOT NULL,
  `num_scenes` INT(11) UNSIGNED NOT NULL)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`levels`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`levels` (
  `scene_id` INT(11) UNSIGNED NOT NULL,
  `level_num` INT(11) UNSIGNED NOT NULL,
  `num_rooms` INT(11) NULL DEFAULT NULL,
  `num_objects` INT(11) NULL DEFAULT NULL,
  `area` DOUBLE NULL DEFAULT NULL,
  PRIMARY KEY (`scene_id`, `level_num`),
  INDEX `for_crowded` (`scene_id` ASC, `num_objects` ASC, `area` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`models`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`models` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `model_id` VARCHAR(30) NOT NULL DEFAULT '',
  `fine_grained_class` VARCHAR(30) NULL DEFAULT NULL,
  `coarse_grained_class` VARCHAR(30) NULL DEFAULT NULL,
  `empty_struct_obj` VARCHAR(30) NULL DEFAULT NULL,
  `nyuv2_40class` VARCHAR(30) NULL DEFAULT NULL,
  `wnsynsetid` VARCHAR(30) NULL DEFAULT NULL,
  `wnsynsetkey` VARCHAR(30) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  INDEX `model_id` (`model_id` ASC),
  INDEX `temp` (`fine_grained_class` ASC, `coarse_grained_class` ASC),
  INDEX `fine_grained_class` (`fine_grained_class` ASC, `model_id` ASC))
ENGINE = InnoDB
AUTO_INCREMENT = 2553
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`objects`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`objects` (
  `scene_id` SMALLINT(11) UNSIGNED NOT NULL,
  `level_num` TINYINT(11) UNSIGNED NOT NULL,
  `room_num` SMALLINT(11) NOT NULL,
  `object_num` SMALLINT(11) UNSIGNED NOT NULL,
  `model_id` VARCHAR(30) NOT NULL DEFAULT '',
  `node_id` VARCHAR(20) NOT NULL DEFAULT '',
  PRIMARY KEY (`scene_id`, `level_num`, `room_num`, `object_num`, `model_id`),
  INDEX `model_id` (`model_id` ASC, `scene_id` ASC, `level_num` ASC, `room_num` ASC),
  INDEX `model_id_2` (`model_id` ASC, `scene_id` ASC, `level_num` ASC, `room_num` ASC, `node_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`pairwise_rels`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`pairwise_rels` (
  `scene_id` SMALLINT(11) UNSIGNED NOT NULL,
  `level_num` TINYINT(11) UNSIGNED NOT NULL,
  `room_num` SMALLINT(11) NOT NULL,
  `primary_object_num` SMALLINT(11) UNSIGNED NOT NULL,
  `secondary_object_num` SMALLINT(11) UNSIGNED NOT NULL,
  `relation_id` TINYINT(11) NOT NULL,
  `primary_id` VARCHAR(30) NOT NULL DEFAULT '',
  `secondary_id` VARCHAR(30) NOT NULL DEFAULT '',
  INDEX `primary_id` (`primary_id` ASC, `secondary_id` ASC, `relation_id` ASC))
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`relations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`relations` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(31) NOT NULL DEFAULT '',
  `definition` VARCHAR(255) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 14
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`room_types`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`room_types` (
  `scene_id` INT(11) NOT NULL,
  `level_num` INT(11) NOT NULL,
  `room_num` INT(11) NOT NULL,
  `room_type_id` INT(11) NOT NULL,
  INDEX `location` (`scene_id` ASC, `level_num` ASC, `room_num` ASC),
  INDEX `room_type_id` (`room_type_id` ASC, `scene_id` ASC, `level_num` ASC, `room_num` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`room_types_names`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`room_types_names` (
  `id` INT(11) UNSIGNED NOT NULL AUTO_INCREMENT,
  `name` VARCHAR(32) NULL DEFAULT NULL,
  PRIMARY KEY (`id`))
ENGINE = InnoDB
AUTO_INCREMENT = 25
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`rooms`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`rooms` (
  `scene_id` INT(10) UNSIGNED NOT NULL,
  `level_num` INT(11) UNSIGNED NOT NULL,
  `room_num` INT(11) NOT NULL,
  `num_objects` INT(11) UNSIGNED NOT NULL,
  `area` DOUBLE UNSIGNED NOT NULL,
  `node_id` VARCHAR(20) NULL DEFAULT NULL,
  PRIMARY KEY (`scene_id`, `level_num`, `room_num`),
  INDEX `area` (`area` ASC),
  INDEX `area_first` (`area` ASC, `scene_id` ASC, `level_num` ASC, `room_num` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `scene_search`.`scenes`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `scene_search`.`scenes` (
  `id` INT(11) NOT NULL,
  `num_levels` INT(11) NOT NULL,
  `num_rooms` INT(11) NOT NULL,
  `num_objects` INT(11) NOT NULL,
  `hash` VARCHAR(32) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
