-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Tempo de geração: 31/05/2025 às 00:41
-- Versão do servidor: 10.4.28-MariaDB
-- Versão do PHP: 8.0.28

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Banco de dados: `sysfit_cli_template`
--

-- --------------------------------------------------------

--
-- Estrutura para tabela `aluno_ficha`
--

CREATE TABLE `aluno_ficha` (
  `AL_FICHA_ID` int(11) NOT NULL,
  `AL_FICHA_USR_ID` int(11) NOT NULL,
  `AL_FICHA_DATA_MATRICULA` date NOT NULL,
  `AL_FICHA_STATUS_MATRICULA` varchar(20) NOT NULL,
  `AL_FICHA_SEXO` char(1) NOT NULL,
  `AL_FICHA_TIPO_SANGUE` varchar(3) DEFAULT NULL,
  `AL_FICHA_PATOLOGIAS` text DEFAULT NULL,
  `AL_FICHA_ALERGIAS` text DEFAULT NULL,
  `AL_FICHA_MEDICAMENTOS` text DEFAULT NULL,
  `AL_FICHA_OBJETIVO_TREINO` text DEFAULT NULL,
  `AL_FICHA_PLANO_ID` int(11) NOT NULL,
  `AL_FICHA_INSTRUTOR_ID` int(11) NOT NULL,
  `AL_FICHA_OBSERVACOES` text DEFAULT NULL,
  `AL_FICHA_FOTO` varchar(255) DEFAULT NULL,
  `AL_FICHA_DATA_CADASTRO` timestamp NOT NULL DEFAULT current_timestamp(),
  `AL_FICHA_DATA_ULTIMA_ATUALIZ` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `AL_FICHA_SERIE_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `avaliacao`
--

CREATE TABLE `avaliacao` (
  `AVAL_ID` int(11) NOT NULL,
  `AVAL_USR_ID` int(11) NOT NULL,
  `AVAL_DATA` date NOT NULL,
  `AVAL_PESO` decimal(5,2) DEFAULT NULL,
  `AVAL_ALTURA` decimal(4,2) DEFAULT NULL,
  `AVAL_IMC` decimal(4,2) DEFAULT NULL,
  `AVAL_PESO_GORDURA` decimal(5,2) DEFAULT NULL,
  `AVAL_PESO_MUSCULAR` decimal(5,2) DEFAULT NULL,
  `AVAL_CINTURA` decimal(5,2) DEFAULT NULL,
  `AVAL_QUADRIL` decimal(5,2) DEFAULT NULL,
  `AVAL_BRACO` decimal(5,2) DEFAULT NULL,
  `AVAL_PERNA` decimal(5,2) DEFAULT NULL,
  `AVAL_FREQUENCIA_CARD` int(11) DEFAULT NULL,
  `AVAL_PRESSAO_SIST` int(11) DEFAULT NULL,
  `AVAL_PRESSAO_DIAST` int(11) DEFAULT NULL,
  `AVAL_IMPEDANCIA` decimal(5,2) DEFAULT NULL,
  `AVAL_OBSERVACOES` text DEFAULT NULL,
  `AVAL_PROFISSIONAL_ID` int(11) NOT NULL,
  `AVAL_DATA_CADASTRO` timestamp NOT NULL DEFAULT current_timestamp(),
  `AVAL_SERIE_ID` int(11) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `documentos`
--

CREATE TABLE `documentos` (
  `DOC_ID` int(11) NOT NULL,
  `DOC_NOME` int(11) NOT NULL,
  `DOC_DESC` varchar(255) DEFAULT NULL,
  `DOC_USR_ID` int(11) NOT NULL,
  `DOC_CAMINHO` varchar(255) DEFAULT NULL,
  `DOC_DATA_CADASTRO` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `exercicio`
--

CREATE TABLE `exercicio` (
  `EX_ID` int(11) NOT NULL,
  `EX_NOME` int(11) NOT NULL,
  `EX_DESCRICAO` text DEFAULT NULL,
  `EX_TIPO` varchar(50) DEFAULT NULL,
  `EX_NIVEL_DIFICULDADE` varchar(50) DEFAULT NULL,
  `EX_DATA_CADASTRO` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `instrutor`
--

CREATE TABLE `instrutor` (
  `INST_ID` int(11) NOT NULL,
  `INST_USR_ID` int(11) NOT NULL,
  `INST_FORMACAO_NIVEL` char(50) NOT NULL,
  `INST_ESPECIALIDADE` char(50) NOT NULL,
  `INST_STATUS` char(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `planos`
--

CREATE TABLE `planos` (
  `PL_ID` int(11) NOT NULL,
  `PL_NOME` varchar(255) NOT NULL,
  `PL_VLR` decimal(10,2) DEFAULT NULL,
  `PL_DATA_CADASTRO` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;



--
-- Estrutura para tabela `serie`
--

CREATE TABLE `serie` (
  `AL_SERIE_ID` int(11) NOT NULL,
  `SR_NOME` varchar(100) NOT NULL,
  `SR_USR_CRIADOR_ID` int(11) NOT NULL,
  `SR_DATA_CRIACAO` timestamp NOT NULL DEFAULT current_timestamp(),
  `SR_DESCRICAO` text DEFAULT NULL,
  `SR_NIVEL_DIFICULDADE` varchar(20) DEFAULT NULL,
  `SR_OBJETIVO` varchar(50) DEFAULT NULL,
  `SR_STATUS` varchar(20) DEFAULT 'ATIVO'
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `serie_detalhe`
--

CREATE TABLE `serie_detalhe` (
  `SR_DET_ID` int(11) NOT NULL,
  `SR_DET_SR_ID` int(11) NOT NULL,
  `SR_DET_USR_CRIADOR_ID` int(11) NOT NULL,
  `SR_DET_EXERCICIO_ID` int(11) NOT NULL,
  `SR_DET_ORDEM` int(11) NOT NULL,
  `SR_DET_REPETICOES` int(11) DEFAULT NULL,
  `SR_DET_SERIES` int(11) DEFAULT NULL,
  `SR_DET_CARGA` decimal(6,2) DEFAULT NULL,
  `SR_DET_INTERVALO_SEG` int(11) DEFAULT NULL,
  `SR_DET_OBSERVACOES` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

-- --------------------------------------------------------

--
-- Estrutura para tabela `usuarios`
--

CREATE TABLE `usuarios` (
  `USR_ID` int(11) NOT NULL,
  `USR_NOME` char(50) NOT NULL,
  `USR_DTA_NASCIMENTO` date NOT NULL,
  `USR_DTA_CADASTRO` datetime DEFAULT current_timestamp(),
  `USR_TIPO` char(20) NOT NULL,
  `USR_LOGIN` char(20) NOT NULL,
  `USR_SENHA` char(255) NOT NULL,
  `USR_TOKEN` varchar(255) DEFAULT NULL,
  `USR_USR_CADASTRO_ID` int(11) NOT NULL,
  `USR_CPF` char(50) NOT NULL,
  `USR_TELEFONE` char(50) NOT NULL,
  `USR_EMAIL` varchar(255) DEFAULT NULL,
  `USR_STATUS` char(1) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_general_ci;

--
-- Despejando dados para a tabela `usuarios`
--

INSERT INTO `usuarios` (`USR_ID`, `USR_NOME`, `USR_DTA_NASCIMENTO`, `USR_DTA_CADASTRO`, `USR_TIPO`, `USR_LOGIN`, `USR_SENHA`, `USR_TOKEN`, `USR_USR_CADASTRO_ID`, `USR_CPF`, `USR_TELEFONE`, `USR_EMAIL`, `USR_STATUS`) VALUES
(4, 'admin', '1990-05-20', '2025-05-22 17:19:44', 'ADM', 'admin', '$2b$12$ZR6YSX.1E4TyyWxf5BptvuFqTNqWk0kGls0cy3qnLQgHeQVxJhsyi', 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJqb2Fvc2lsdmEifQ.kB3PBCB6U4W0cD8DO6u6vUijz0K9bzfzDJ6aKVLtzAc', 1, '123.456.789-01', '(31) 99999-9999', 'admin@example.com', 'A');

--
-- Índices para tabelas despejadas
--

--
-- Índices de tabela `aluno_ficha`
--
ALTER TABLE `aluno_ficha`
  ADD PRIMARY KEY (`AL_FICHA_ID`);

--
-- Índices de tabela `avaliacao`
--
ALTER TABLE `avaliacao`
  ADD PRIMARY KEY (`AVAL_ID`);

--
-- Índices de tabela `documentos`
--
ALTER TABLE `documentos`
  ADD PRIMARY KEY (`DOC_ID`);

--
-- Índices de tabela `exercicio`
--
ALTER TABLE `exercicio`
  ADD PRIMARY KEY (`EX_ID`);

--
-- Índices de tabela `instrutor`
--
ALTER TABLE `instrutor`
  ADD PRIMARY KEY (`INST_ID`);

--
-- Índices de tabela `planos`
--
ALTER TABLE `planos`
  ADD PRIMARY KEY (`PL_ID`);

--
-- Índices de tabela `serie`
--
ALTER TABLE `serie`
  ADD PRIMARY KEY (`AL_SERIE_ID`);

--
-- Índices de tabela `serie_detalhe`
--
ALTER TABLE `serie_detalhe`
  ADD PRIMARY KEY (`SR_DET_ID`);

--
-- Índices de tabela `usuarios`
--
ALTER TABLE `usuarios`
  ADD PRIMARY KEY (`USR_ID`),
  ADD UNIQUE KEY `unq_login` (`USR_LOGIN`),
  ADD UNIQUE KEY `uniq_cpf` (`USR_CPF`),
  ADD UNIQUE KEY `uniq_email` (`USR_EMAIL`);

--
-- AUTO_INCREMENT para tabelas despejadas
--

--
-- AUTO_INCREMENT de tabela `avaliacao`
--
ALTER TABLE `avaliacao`
  MODIFY `AVAL_ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `serie`
--
ALTER TABLE `serie`
  MODIFY `AL_SERIE_ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `serie_detalhe`
--
ALTER TABLE `serie_detalhe`
  MODIFY `SR_DET_ID` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT de tabela `usuarios`
--
ALTER TABLE `usuarios`
  MODIFY `USR_ID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=11;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
