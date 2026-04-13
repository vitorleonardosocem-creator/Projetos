-- Executar este script no SQL Server Management Studio
-- Base de dados: Visitantes

USE [Visitantes];
GO

CREATE TABLE dbo.AlmocoPresencas (
    Id            INT IDENTITY(1,1) PRIMARY KEY,
    IdVisitante   INT          NOT NULL,
    TipoVisitante VARCHAR(20)  NOT NULL,   -- 'Cliente' ou 'Fornecedor'
    Data          DATE         NOT NULL,
    Presente      BIT          NOT NULL DEFAULT 0,
    DataMarcacao  DATETIME              DEFAULT GETDATE()
);
GO

-- Índice para acelerar as queries por data
CREATE INDEX IX_AlmocoPresencas_Data
    ON dbo.AlmocoPresencas (Data, TipoVisitante);
GO

PRINT 'Tabela AlmocoPresencas criada com sucesso.';
