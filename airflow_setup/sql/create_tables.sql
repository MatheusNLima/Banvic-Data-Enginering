/*

DROP TABLE IF EXISTS public.agencias;
DROP TABLE IF EXISTS public.clientes;
DROP TABLE IF EXISTS public.colaborador_agencia;
DROP TABLE IF EXISTS public.colaboradores;
DROP TABLE IF EXISTS public.contas;
DROP TABLE IF EXISTS public.propostas_credito;
DROP TABLE IF EXISTS public.transacoes;

*/

-- Função temporária para criar ENUMs de forma idempotente
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_proposta') THEN
        CREATE TYPE public.status_proposta AS ENUM (
            'Enviada',
            'Validação documentos',
            'Aprovada',
            'Reprovada',
            'Em análise'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_agencia') THEN
        CREATE TYPE public.tipo_agencia AS ENUM (
            'Digital',
            'Física'
        );
    END IF;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_cliente') THEN
        CREATE TYPE public.tipo_cliente AS ENUM (
            'PF',
            'PJ'
        );
    END IF;
END$$;

-- Criação das tabelas do banco de origem
CREATE TABLE IF NOT EXISTS public.agencias (
    cod_agencia integer NOT NULL,
    nome character varying(255) NOT NULL,
    endereco text,
    cidade character varying(255),
    uf character(2),
    data_abertura date,
    tipo_agencia public.tipo_agencia
);

CREATE TABLE IF NOT EXISTS public.clientes (
    cod_cliente integer NOT NULL,
    primeiro_nome character varying(255) NOT NULL,
    ultimo_nome character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    tipo_cliente public.tipo_cliente,
    data_inclusao timestamp with time zone,
    cpfcnpj character varying(18) NOT NULL,
    data_nascimento date,
    endereco text,
    cep character varying(9)
);

CREATE TABLE IF NOT EXISTS public.colaborador_agencia (
    cod_colaborador integer NOT NULL,
    cod_agencia integer NOT NULL
);

CREATE TABLE IF NOT EXISTS public.colaboradores (
    cod_colaborador integer NOT NULL,
    primeiro_nome character varying(255) NOT NULL,
    ultimo_nome character varying(255) NOT NULL,
    email character varying(255) NOT NULL,
    cpf character varying(14) NOT NULL,
    data_nascimento date,
    endereco text,
    cep character varying(9)
);

CREATE TABLE IF NOT EXISTS public.contas (
    num_conta bigint NOT NULL,
    cod_cliente integer,
    cod_agencia integer,
    cod_colaborador integer,
    tipo_conta public.tipo_cliente,
    data_abertura timestamp with time zone,
    saldo_total numeric(15,2),
    saldo_disponivel numeric(15,2),
    data_ultimo_lancamento timestamp with time zone
);

CREATE TABLE IF NOT EXISTS public.propostas_credito (
    cod_proposta integer NOT NULL,
    cod_cliente integer,
    cod_colaborador integer,
    data_entrada_proposta timestamp with time zone,
    taxa_juros_mensal numeric(5,4),
    valor_proposta numeric(15,2),
    valor_financiamento numeric(15,2),
    valor_entrada numeric(15,2),
    valor_prestacao numeric(15,2),
    quantidade_parcelas integer,
    carencia integer,
    status_proposta public.status_proposta
);

-- Criação da tabela para o arquivo CSV de transações
CREATE TABLE IF NOT EXISTS public.transacoes (
    id VARCHAR(255),
    conta_id BIGINT,
    data_transacao TIMESTAMP WITH TIME ZONE,
    tipo_transacao VARCHAR(255),
    valor NUMERIC(15, 2)
);