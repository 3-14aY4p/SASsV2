SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `db_SmartAttendance`
--

-- --------------------------------------------------------

--
-- Table structure for table `tbl_instructor`
--

CREATE TABLE `tbl_instructor` (
  `instructor_id` varchar(20) NOT NULL,
  `instructor_name` varchar(130) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_subject`
--

CREATE TABLE `tbl_subject` (
  `subject_id` varchar(20) NOT NULL,
  `subject_title` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_student`
--

CREATE TABLE `tbl_student` (
  `student_id` varchar(20) NOT NULL,
  `student_name` varchar(130) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;


-- --------------------------------------------------------

--
-- Table structure for table `tbl_enrollment`
--

CREATE TABLE `tbl_enrollment` (
  `enrollment_id` int(11) NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `semester` varchar(20) DEFAULT NULL,
  `school_year` varchar(20) DEFAULT NULL,
  `course` varchar(20) DEFAULT NULL,
  `year_level` int(11) DEFAULT NULL,
  `section` char(1) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_subjects_enrolled`
--

CREATE TABLE `tbl_subjects_enrolled` (
  `enrollment_id` int(11) NOT NULL,
  `subject_id` varchar(20) DEFAULT NULL,
  `instructor_id`varchar(20) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `tbl_attendance`
--

CREATE TABLE `tbl_attendance` (
  `attendance_id` int(11) NOT NULL,
  `subject_id` varchar(20) DEFAULT NULL,
  `instructor_id` varchar(20) DEFAULT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `date` date DEFAULT curdate(),
  `time` time DEFAULT curtime(),
  `class_start` time DEFAULT NULL,
  `class_end` time DEFAULT NULL,
  `attendance_status` varchar(20) DEFAULT "Absent"
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Indexes for dumped tables
--


--
-- Indexes for table `instructor`
--
ALTER TABLE `tbl_instructor`
  ADD PRIMARY KEY (`instructor_id`);

--
-- Indexes for table `subject`
--
ALTER TABLE `tbl_subject`
  ADD PRIMARY KEY (`subject_id`);

--
-- Indexes for table `student`
--
ALTER TABLE `tbl_student`
  ADD PRIMARY KEY (`student_id`);

--
-- Indexes for table `tbl_enrollment`
--
ALTER TABLE `tbl_enrollment`
  ADD PRIMARY KEY (`enrollment_id`),
  ADD KEY `student_id` (`student_id`);

--
-- Indexes for table `subjects_enrolled`
--
ALTER TABLE `tbl_subjects_enrolled`
  ADD KEY `enrollment_id` (`enrollment_id`),
  ADD KEY `subject_id` (`subject_id`),
  ADD KEY `instructor_id` (`instructor_id`);

--
-- Indexes for table `tbl_attendance`
--
ALTER TABLE `tbl_attendance`
  ADD PRIMARY KEY (`attendance_id`),
  ADD KEY `subject_id` (`subject_id`),
  ADD KEY `instructor_id` (`instructor_id`),
  ADD KEY `student_id` (`student_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `attendance`
--
ALTER TABLE `tbl_attendance`
  MODIFY `attendance_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `enrollment`
--
ALTER TABLE `tbl_enrollment`
  MODIFY `enrollment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=40;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `tbl_attendance`
--
ALTER TABLE `tbl_attendance`
  ADD CONSTRAINT `tbl_attendance_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `tbl_student` (`student_id`),
  ADD CONSTRAINT `tbl_attendance_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `tbl_subject` (`subject_id`),
  ADD CONSTRAINT `tbl_attendance_ibfk_3` FOREIGN KEY (`instructor_id`) REFERENCES `tbl_instructor` (`instructor_id`);
  
--
-- Constraints for table `tbl_enrollment`
--
ALTER TABLE `tbl_enrollment`
  ADD CONSTRAINT `tbl_enrollment_ibfk_1` FOREIGN KEY (`student_id`) REFERENCES `tbl_student` (`student_id`);

--
-- Constraints for table `tbl_subjects_enrolled`
--
ALTER TABLE `tbl_subjects_enrolled`
  ADD CONSTRAINT `tbl_subjects_enrolled_ibfk_1` FOREIGN KEY (`enrollment_id`) REFERENCES `tbl_enrollment` (`enrollment_id`),
  ADD CONSTRAINT `tbl_subjects_enrolled_ibfk_2` FOREIGN KEY (`subject_id`) REFERENCES `tbl_subject` (`subject_id`),
  ADD CONSTRAINT `tbl_subjects_enrolled_ibfk_3` FOREIGN KEY (`instructor_id`) REFERENCES `tbl_instructor` (`instructor_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
