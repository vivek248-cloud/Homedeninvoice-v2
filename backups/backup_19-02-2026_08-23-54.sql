-- MySQL dump 10.13  Distrib 8.0.45, for Linux (x86_64)
--
-- Host: localhost    Database: homedeninvoice_db
-- ------------------------------------------------------
-- Server version	8.0.45-0ubuntu0.22.04.1

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `admin_interface_theme`
--

DROP TABLE IF EXISTS `admin_interface_theme`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `admin_interface_theme` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `active` tinyint(1) NOT NULL,
  `title` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_visible` tinyint(1) NOT NULL,
  `logo` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo_visible` tinyint(1) NOT NULL,
  `css_header_background_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `title_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_header_text_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_header_link_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_header_link_hover_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_module_background_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_module_text_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_module_link_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_module_link_hover_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_module_rounded_corners` tinyint(1) NOT NULL,
  `css_generic_link_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_generic_link_hover_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_save_button_background_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_save_button_background_hover_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_save_button_text_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_delete_button_background_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_delete_button_background_hover_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_delete_button_text_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `list_filter_dropdown` tinyint(1) NOT NULL,
  `related_modal_active` tinyint(1) NOT NULL,
  `related_modal_background_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_modal_rounded_corners` tinyint(1) NOT NULL,
  `logo_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `recent_actions_visible` tinyint(1) NOT NULL,
  `favicon` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `related_modal_background_opacity` varchar(5) COLLATE utf8mb4_unicode_ci NOT NULL,
  `env_name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `env_visible_in_header` tinyint(1) NOT NULL,
  `env_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `env_visible_in_favicon` tinyint(1) NOT NULL,
  `related_modal_close_button_visible` tinyint(1) NOT NULL,
  `language_chooser_active` tinyint(1) NOT NULL,
  `language_chooser_display` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `list_filter_sticky` tinyint(1) NOT NULL,
  `form_pagination_sticky` tinyint(1) NOT NULL,
  `form_submit_sticky` tinyint(1) NOT NULL,
  `css_module_background_selected_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `css_module_link_selected_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `logo_max_height` smallint unsigned NOT NULL,
  `logo_max_width` smallint unsigned NOT NULL,
  `foldable_apps` tinyint(1) NOT NULL,
  `language_chooser_control` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `list_filter_highlight` tinyint(1) NOT NULL,
  `list_filter_removal_links` tinyint(1) NOT NULL,
  `show_fieldsets_as_tabs` tinyint(1) NOT NULL,
  `show_inlines_as_tabs` tinyint(1) NOT NULL,
  `css_generic_link_active_color` varchar(10) COLLATE utf8mb4_unicode_ci NOT NULL,
  `collapsible_stacked_inlines` tinyint(1) NOT NULL,
  `collapsible_stacked_inlines_collapsed` tinyint(1) NOT NULL,
  `collapsible_tabular_inlines` tinyint(1) NOT NULL,
  `collapsible_tabular_inlines_collapsed` tinyint(1) NOT NULL,
  `form_actions_sticky` tinyint(1) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `admin_interface_theme_name_30bda70f_uniq` (`name`),
  CONSTRAINT `admin_interface_theme_chk_1` CHECK ((`logo_max_height` >= 0)),
  CONSTRAINT `admin_interface_theme_chk_2` CHECK ((`logo_max_width` >= 0))
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admin_interface_theme`
--

LOCK TABLES `admin_interface_theme` WRITE;
/*!40000 ALTER TABLE `admin_interface_theme` DISABLE KEYS */;
INSERT INTO `admin_interface_theme` VALUES (1,'Django',1,'Django administration',1,'',1,'#0C4B33','#F5DD5D','#44B78B','#FFFFFF','#C9F0DD','#44B78B','#FFFFFF','#FFFFFF','#C9F0DD',1,'#0C3C26','#156641','#0C4B33','#0C3C26','#FFFFFF','#BA2121','#A41515','#FFFFFF',1,1,'#000000',1,'#FFFFFF',1,'','0.3','',1,'#E74C3C',1,1,1,'code',1,1,1,'#FFFFCC','#FFFFFF',100,400,1,'default-select',1,1,0,0,'#29B864',0,1,0,1,1);
/*!40000 ALTER TABLE `admin_interface_theme` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `group_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int NOT NULL,
  `codename` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add Theme',1,'add_theme'),(2,'Can change Theme',1,'change_theme'),(3,'Can delete Theme',1,'delete_theme'),(4,'Can view Theme',1,'view_theme'),(5,'Can add client',2,'add_client'),(6,'Can change client',2,'change_client'),(7,'Can delete client',2,'delete_client'),(8,'Can view client',2,'view_client'),(9,'Can add floor type',3,'add_floortype'),(10,'Can change floor type',3,'change_floortype'),(11,'Can delete floor type',3,'delete_floortype'),(12,'Can view floor type',3,'view_floortype'),(13,'Can add full semi',4,'add_fullsemi'),(14,'Can change full semi',4,'change_fullsemi'),(15,'Can delete full semi',4,'delete_fullsemi'),(16,'Can view full semi',4,'view_fullsemi'),(17,'Can add room type',5,'add_roomtype'),(18,'Can change room type',5,'change_roomtype'),(19,'Can delete room type',5,'delete_roomtype'),(20,'Can view room type',5,'view_roomtype'),(21,'Can add project',6,'add_project'),(22,'Can change project',6,'change_project'),(23,'Can delete project',6,'delete_project'),(24,'Can view project',6,'view_project'),(25,'Can add payment',7,'add_payment'),(26,'Can change payment',7,'change_payment'),(27,'Can delete payment',7,'delete_payment'),(28,'Can view payment',7,'view_payment'),(29,'Can add spend',8,'add_spend'),(30,'Can change spend',8,'change_spend'),(31,'Can delete spend',8,'delete_spend'),(32,'Can view spend',8,'view_spend'),(33,'Can add log entry',9,'add_logentry'),(34,'Can change log entry',9,'change_logentry'),(35,'Can delete log entry',9,'delete_logentry'),(36,'Can view log entry',9,'view_logentry'),(37,'Can add permission',10,'add_permission'),(38,'Can change permission',10,'change_permission'),(39,'Can delete permission',10,'delete_permission'),(40,'Can view permission',10,'view_permission'),(41,'Can add group',11,'add_group'),(42,'Can change group',11,'change_group'),(43,'Can delete group',11,'delete_group'),(44,'Can view group',11,'view_group'),(45,'Can add user',12,'add_user'),(46,'Can change user',12,'change_user'),(47,'Can delete user',12,'delete_user'),(48,'Can view user',12,'view_user'),(49,'Can add content type',13,'add_contenttype'),(50,'Can change content type',13,'change_contenttype'),(51,'Can delete content type',13,'delete_contenttype'),(52,'Can view content type',13,'view_contenttype'),(53,'Can add session',14,'add_session'),(54,'Can change session',14,'change_session'),(55,'Can delete session',14,'delete_session'),(56,'Can view session',14,'view_session');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `first_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `last_name` varchar(150) COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
INSERT INTO `auth_user` VALUES (1,'pbkdf2_sha256$1000000$lKFJYmIvp9KyWGmj2NzRha$+bpuYmPVloNLS2GHm7ikoC9Dop6oqiasHRXIlIUGyog=','2026-02-19 07:43:52.216699',1,'admin','','','admin@gmail.com',1,1,'2026-02-19 05:51:38.537755');
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `user_id` int NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_client`
--

DROP TABLE IF EXISTS `billing_client`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_client` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mobile_1` varchar(15) COLLATE utf8mb4_unicode_ci NOT NULL,
  `mobile_2` varchar(15) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `address` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `email` varchar(254) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `notes` longtext COLLATE utf8mb4_unicode_ci,
  `gst_number` varchar(30) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `discount` decimal(5,2) NOT NULL,
  `created_at` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_client`
--

LOCK TABLES `billing_client` WRITE;
/*!40000 ALTER TABLE `billing_client` DISABLE KEYS */;
INSERT INTO `billing_client` VALUES (1,'Vivek','9786224099','9786224099','123 street','vivekofficial248@gmail.com','test','18',0.00,'2026-02-19 08:01:59.063017');
/*!40000 ALTER TABLE `billing_client` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_floortype`
--

DROP TABLE IF EXISTS `billing_floortype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_floortype` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_floortype`
--

LOCK TABLES `billing_floortype` WRITE;
/*!40000 ALTER TABLE `billing_floortype` DISABLE KEYS */;
/*!40000 ALTER TABLE `billing_floortype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_fullsemi`
--

DROP TABLE IF EXISTS `billing_fullsemi`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_fullsemi` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_fullsemi`
--

LOCK TABLES `billing_fullsemi` WRITE;
/*!40000 ALTER TABLE `billing_fullsemi` DISABLE KEYS */;
/*!40000 ALTER TABLE `billing_fullsemi` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_payment`
--

DROP TABLE IF EXISTS `billing_payment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_payment` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `amount` decimal(12,2) NOT NULL,
  `payment_mode` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `date` date NOT NULL,
  `project_id` bigint NOT NULL,
  `invoice_token` char(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `invoice_token` (`invoice_token`),
  KEY `billing_payment_project_id_5e335293_fk_billing_project_id` (`project_id`),
  CONSTRAINT `billing_payment_project_id_5e335293_fk_billing_project_id` FOREIGN KEY (`project_id`) REFERENCES `billing_project` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_payment`
--

LOCK TABLES `billing_payment` WRITE;
/*!40000 ALTER TABLE `billing_payment` DISABLE KEYS */;
/*!40000 ALTER TABLE `billing_payment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_project`
--

DROP TABLE IF EXISTS `billing_project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_project` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `budget` decimal(12,2) NOT NULL,
  `status` varchar(20) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `client_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `billing_project_client_id_04791a11_fk_billing_client_id` (`client_id`),
  CONSTRAINT `billing_project_client_id_04791a11_fk_billing_client_id` FOREIGN KEY (`client_id`) REFERENCES `billing_client` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_project`
--

LOCK TABLES `billing_project` WRITE;
/*!40000 ALTER TABLE `billing_project` DISABLE KEYS */;
INSERT INTO `billing_project` VALUES (1,'HD01',0.00,'ongoing','2026-02-19 08:02:23.492821',1);
/*!40000 ALTER TABLE `billing_project` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_roomtype`
--

DROP TABLE IF EXISTS `billing_roomtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_roomtype` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `name` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_roomtype`
--

LOCK TABLES `billing_roomtype` WRITE;
/*!40000 ALTER TABLE `billing_roomtype` DISABLE KEYS */;
/*!40000 ALTER TABLE `billing_roomtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `billing_spend`
--

DROP TABLE IF EXISTS `billing_spend`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `billing_spend` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `description` longtext COLLATE utf8mb4_unicode_ci,
  `length` decimal(10,2) DEFAULT NULL,
  `width` decimal(10,2) DEFAULT NULL,
  `area` decimal(12,2) DEFAULT NULL,
  `unit` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,
  `created_at` datetime(6) NOT NULL,
  `fullsemi_id` bigint DEFAULT NULL,
  `floor_id` bigint DEFAULT NULL,
  `project_id` bigint NOT NULL,
  `room_id` bigint DEFAULT NULL,
  `rate` decimal(12,2) DEFAULT NULL,
  `qty` decimal(10,2) NOT NULL,
  `elements` varchar(200) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `billing_spend_floor_id_722aaa18_fk_billing_floortype_id` (`floor_id`),
  KEY `billing_spend_project_id_f44a9d52_fk_billing_project_id` (`project_id`),
  KEY `billing_spend_room_id_71bf7d18_fk_billing_roomtype_id` (`room_id`),
  KEY `billing_spend_fullsemi_id_97e23b3f_fk_billing_fullsemi_id` (`fullsemi_id`),
  CONSTRAINT `billing_spend_floor_id_722aaa18_fk_billing_floortype_id` FOREIGN KEY (`floor_id`) REFERENCES `billing_floortype` (`id`),
  CONSTRAINT `billing_spend_fullsemi_id_97e23b3f_fk_billing_fullsemi_id` FOREIGN KEY (`fullsemi_id`) REFERENCES `billing_fullsemi` (`id`),
  CONSTRAINT `billing_spend_project_id_f44a9d52_fk_billing_project_id` FOREIGN KEY (`project_id`) REFERENCES `billing_project` (`id`),
  CONSTRAINT `billing_spend_room_id_71bf7d18_fk_billing_roomtype_id` FOREIGN KEY (`room_id`) REFERENCES `billing_roomtype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `billing_spend`
--

LOCK TABLES `billing_spend` WRITE;
/*!40000 ALTER TABLE `billing_spend` DISABLE KEYS */;
/*!40000 ALTER TABLE `billing_spend` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext COLLATE utf8mb4_unicode_ci,
  `object_repr` varchar(200) COLLATE utf8mb4_unicode_ci NOT NULL,
  `action_flag` smallint unsigned NOT NULL,
  `change_message` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `content_type_id` int DEFAULT NULL,
  `user_id` int NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `django_admin_log_chk_1` CHECK ((`action_flag` >= 0))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  `model` varchar(100) COLLATE utf8mb4_unicode_ci NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (9,'admin','logentry'),(1,'admin_interface','theme'),(11,'auth','group'),(10,'auth','permission'),(12,'auth','user'),(2,'billing','client'),(3,'billing','floortype'),(4,'billing','fullsemi'),(7,'billing','payment'),(6,'billing','project'),(5,'billing','roomtype'),(8,'billing','spend'),(13,'contenttypes','contenttype'),(14,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` bigint NOT NULL AUTO_INCREMENT,
  `app` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `name` varchar(255) COLLATE utf8mb4_unicode_ci NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=57 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2026-02-19 05:50:38.538240'),(2,'auth','0001_initial','2026-02-19 05:50:39.476315'),(3,'admin','0001_initial','2026-02-19 05:50:39.652873'),(4,'admin','0002_logentry_remove_auto_add','2026-02-19 05:50:39.662694'),(5,'admin','0003_logentry_add_action_flag_choices','2026-02-19 05:50:39.678469'),(6,'admin_interface','0001_initial','2026-02-19 05:50:39.714777'),(7,'admin_interface','0002_add_related_modal','2026-02-19 05:50:39.931869'),(8,'admin_interface','0003_add_logo_color','2026-02-19 05:50:40.045214'),(9,'admin_interface','0004_rename_title_color','2026-02-19 05:50:40.083574'),(10,'admin_interface','0005_add_recent_actions_visible','2026-02-19 05:50:40.127684'),(11,'admin_interface','0006_bytes_to_str','2026-02-19 05:50:40.166940'),(12,'admin_interface','0007_add_favicon','2026-02-19 05:50:40.232813'),(13,'admin_interface','0008_change_related_modal_background_opacity_type','2026-02-19 05:50:40.345493'),(14,'admin_interface','0009_add_enviroment','2026-02-19 05:50:40.492492'),(15,'admin_interface','0010_add_localization','2026-02-19 05:50:40.507664'),(16,'admin_interface','0011_add_environment_options','2026-02-19 05:50:40.699071'),(17,'admin_interface','0012_update_verbose_names','2026-02-19 05:50:40.711028'),(18,'admin_interface','0013_add_related_modal_close_button','2026-02-19 05:50:40.766199'),(19,'admin_interface','0014_name_unique','2026-02-19 05:50:40.793199'),(20,'admin_interface','0015_add_language_chooser_active','2026-02-19 05:50:40.853275'),(21,'admin_interface','0016_add_language_chooser_display','2026-02-19 05:50:40.911940'),(22,'admin_interface','0017_change_list_filter_dropdown','2026-02-19 05:50:40.916631'),(23,'admin_interface','0018_theme_list_filter_sticky','2026-02-19 05:50:40.974132'),(24,'admin_interface','0019_add_form_sticky','2026-02-19 05:50:41.086584'),(25,'admin_interface','0020_module_selected_colors','2026-02-19 05:50:41.217740'),(26,'admin_interface','0021_file_extension_validator','2026-02-19 05:50:41.224202'),(27,'admin_interface','0022_add_logo_max_width_and_height','2026-02-19 05:50:41.488449'),(28,'admin_interface','0023_theme_foldable_apps','2026-02-19 05:50:41.600950'),(29,'admin_interface','0024_remove_theme_css','2026-02-19 05:50:41.666745'),(30,'admin_interface','0025_theme_language_chooser_control','2026-02-19 05:50:41.725243'),(31,'admin_interface','0026_theme_list_filter_highlight','2026-02-19 05:50:41.775084'),(32,'admin_interface','0027_theme_list_filter_removal_links','2026-02-19 05:50:41.829036'),(33,'admin_interface','0028_theme_show_fieldsets_as_tabs_and_more','2026-02-19 05:50:41.935532'),(34,'admin_interface','0029_theme_css_generic_link_active_color','2026-02-19 05:50:41.988579'),(35,'admin_interface','0030_theme_collapsible_stacked_inlines_and_more','2026-02-19 05:50:42.220100'),(36,'admin_interface','0031_theme_form_actions_sticky','2026-02-19 05:50:42.280451'),(37,'admin_interface','0032_alter_theme_defaults','2026-02-19 05:50:42.297817'),(38,'contenttypes','0002_remove_content_type_name','2026-02-19 05:50:42.396491'),(39,'auth','0002_alter_permission_name_max_length','2026-02-19 05:50:42.447958'),(40,'auth','0003_alter_user_email_max_length','2026-02-19 05:50:42.501418'),(41,'auth','0004_alter_user_username_opts','2026-02-19 05:50:42.513421'),(42,'auth','0005_alter_user_last_login_null','2026-02-19 05:50:42.594848'),(43,'auth','0006_require_contenttypes_0002','2026-02-19 05:50:42.600723'),(44,'auth','0007_alter_validators_add_error_messages','2026-02-19 05:50:42.623240'),(45,'auth','0008_alter_user_username_max_length','2026-02-19 05:50:42.763434'),(46,'auth','0009_alter_user_last_name_max_length','2026-02-19 05:50:42.890646'),(47,'auth','0010_alter_group_name_max_length','2026-02-19 05:50:42.936086'),(48,'auth','0011_update_proxy_permissions','2026-02-19 05:50:42.960344'),(49,'auth','0012_alter_user_first_name_max_length','2026-02-19 05:50:43.038322'),(50,'billing','0001_initial','2026-02-19 05:50:43.761352'),(51,'billing','0002_alter_spend_entity_alter_spend_floor_and_more','2026-02-19 05:50:43.788655'),(52,'billing','0003_remove_spend_price_spend_rate','2026-02-19 05:50:43.996402'),(53,'billing','0004_spend_qty','2026-02-19 05:50:44.115249'),(54,'billing','0005_rename_entity_spend_fullsemi_spend_elements','2026-02-19 05:50:44.349415'),(55,'billing','0006_payment_invoice_token','2026-02-19 05:50:44.408827'),(56,'sessions','0001_initial','2026-02-19 05:50:44.469429');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) COLLATE utf8mb4_unicode_ci NOT NULL,
  `session_data` longtext COLLATE utf8mb4_unicode_ci NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
INSERT INTO `django_session` VALUES ('qlp1bfa8a0wo151wgd4zal8y33ix02l8','.eJxVjEEOwiAQRe_C2pAyMwi4dO8ZyMCgVA1NSrsy3l2bdKHb_977LxV5XWpce5njKOqkjDr8bonzo7QNyJ3bbdJ5ass8Jr0peqddXyYpz_Pu_h1U7vVbo0FrwxGJC3hIFq_ZkYFUAHEAziHg4AuRGANZJBA7J57IU_CSU1DvD7GgNug:1vsyhU:8bq17buCRTqXPslXrt6Nt2DhtztORpm-1l2fLX5pkcc','2026-03-05 07:43:52.252635');
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-02-19  8:23:54
