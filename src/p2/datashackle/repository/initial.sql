-- phpMyAdmin SQL Dump
-- version 3.2.4
-- http://www.phpmyadmin.net
--
-- Host: localhost
-- Generation Time: Nov 04, 2011 at 10:08 AM
-- Server version: 5.1.44
-- PHP Version: 5.3.1

SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `datashackle`
--

-- --------------------------------------------------------

--
-- Table structure for table `p2_sqlmigrate`
--

CREATE TABLE IF NOT EXISTS `p2_sqlmigrate` (
  `repository_id` varchar(64) NOT NULL,
  `repository_path` varchar(255) NOT NULL,
  `version` int(11) NOT NULL,
  PRIMARY KEY (`repository_id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `p2_sqlmigrate`
--

INSERT INTO `p2_sqlmigrate` (`repository_id`, `repository_path`, `version`) VALUES
('landpuls.de', '/Users/michaeljenny/projects/landpuls.de/src/p2.datashackle.repository/src/p2/datashackle/repository', 0);

-- --------------------------------------------------------

--
-- Table structure for table `story`
--

CREATE TABLE IF NOT EXISTS `story` (
  `id` varchar(8) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=MyISAM DEFAULT CHARSET=latin1;

--
-- Dumping data for table `story`
--

