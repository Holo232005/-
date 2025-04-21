--
-- PostgreSQL database dump
--

-- Dumped from database version 16.7
-- Dumped by pg_dump version 16.7

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: prevent_self_coaching(); Type: FUNCTION; Schema: public; Owner: sportschool
--

CREATE FUNCTION public.prevent_self_coaching() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    IF EXISTS (
        SELECT 1 
        FROM coaches c
        JOIN students s ON c.user_id = s.user_id
        WHERE c.id = NEW.coach_id AND s.id = NEW.student_id
    ) THEN
        RAISE EXCEPTION 'Тренер не может быть студентом для самого себя';
    END IF;
    RETURN NEW;
END;
$$;


ALTER FUNCTION public.prevent_self_coaching() OWNER TO sportschool;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administration; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.administration (
    id integer NOT NULL,
    user_id integer,
    full_name character varying(255) NOT NULL,
    "position" character varying(255),
    contact_info text
);


ALTER TABLE public.administration OWNER TO sportschool;

--
-- Name: administration_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.administration_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.administration_id_seq OWNER TO sportschool;

--
-- Name: administration_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.administration_id_seq OWNED BY public.administration.id;


--
-- Name: coaches; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.coaches (
    id integer NOT NULL,
    user_id integer,
    full_name character varying(255) NOT NULL,
    specialization character varying(255),
    contact_info text
);


ALTER TABLE public.coaches OWNER TO sportschool;

--
-- Name: coaches_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.coaches_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.coaches_id_seq OWNER TO sportschool;

--
-- Name: coaches_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.coaches_id_seq OWNED BY public.coaches.id;


--
-- Name: competitions; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.competitions (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    event_date timestamp without time zone NOT NULL,
    location character varying(255)
);


ALTER TABLE public.competitions OWNER TO sportschool;

--
-- Name: competitions_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.competitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.competitions_id_seq OWNER TO sportschool;

--
-- Name: competitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.competitions_id_seq OWNED BY public.competitions.id;


--
-- Name: inventory; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.inventory (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    description text,
    quantity integer NOT NULL,
    location character varying(255),
    CONSTRAINT inventory_quantity_check CHECK ((quantity >= 0))
);


ALTER TABLE public.inventory OWNER TO sportschool;

--
-- Name: inventory_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.inventory_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_id_seq OWNER TO sportschool;

--
-- Name: inventory_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.inventory_id_seq OWNED BY public.inventory.id;


--
-- Name: inventory_movements; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.inventory_movements (
    id integer NOT NULL,
    inventory_id integer,
    student_id integer,
    coach_id integer,
    movement_type character varying(50),
    destination character varying(255),
    movement_date character varying,
    CONSTRAINT inventory_movements_movement_type_check CHECK (((movement_type)::text = ANY ((ARRAY['issued'::character varying, 'returned'::character varying, 'transferred'::character varying])::text[])))
);


ALTER TABLE public.inventory_movements OWNER TO sportschool;

--
-- Name: inventory_movements_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.inventory_movements_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.inventory_movements_id_seq OWNER TO sportschool;

--
-- Name: inventory_movements_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.inventory_movements_id_seq OWNED BY public.inventory_movements.id;


--
-- Name: schedule; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.schedule (
    id integer NOT NULL,
    student_id integer,
    coach_id integer,
    class_date timestamp without time zone NOT NULL,
    location character varying(255)
);


ALTER TABLE public.schedule OWNER TO sportschool;

--
-- Name: schedule_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.schedule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.schedule_id_seq OWNER TO sportschool;

--
-- Name: schedule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.schedule_id_seq OWNED BY public.schedule.id;


--
-- Name: student_competitions; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.student_competitions (
    id integer NOT NULL,
    student_id integer,
    competition_id integer,
    inventory_id integer
);


ALTER TABLE public.student_competitions OWNER TO sportschool;

--
-- Name: student_competitions_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.student_competitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.student_competitions_id_seq OWNER TO sportschool;

--
-- Name: student_competitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.student_competitions_id_seq OWNED BY public.student_competitions.id;


--
-- Name: students; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.students (
    id integer NOT NULL,
    user_id integer,
    full_name character varying(255) NOT NULL,
    birth_date date NOT NULL,
    contact_info text,
    registration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    completed_lessons integer DEFAULT 0
);


ALTER TABLE public.students OWNER TO sportschool;

--
-- Name: students_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.students_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.students_id_seq OWNER TO sportschool;

--
-- Name: students_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.students_id_seq OWNED BY public.students.id;


--
-- Name: users; Type: TABLE; Schema: public; Owner: sportschool
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying(255) NOT NULL,
    password_hash character varying(255) NOT NULL,
    role character varying(50) NOT NULL,
    CONSTRAINT users_role_check CHECK (((role)::text = ANY ((ARRAY['coacher'::character varying, 'administration'::character varying, 'student'::character varying])::text[])))
);


ALTER TABLE public.users OWNER TO sportschool;

--
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: sportschool
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO sportschool;

--
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: sportschool
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- Name: administration id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.administration ALTER COLUMN id SET DEFAULT nextval('public.administration_id_seq'::regclass);


--
-- Name: coaches id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.coaches ALTER COLUMN id SET DEFAULT nextval('public.coaches_id_seq'::regclass);


--
-- Name: competitions id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.competitions ALTER COLUMN id SET DEFAULT nextval('public.competitions_id_seq'::regclass);


--
-- Name: inventory id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory ALTER COLUMN id SET DEFAULT nextval('public.inventory_id_seq'::regclass);


--
-- Name: inventory_movements id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory_movements ALTER COLUMN id SET DEFAULT nextval('public.inventory_movements_id_seq'::regclass);


--
-- Name: schedule id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.schedule ALTER COLUMN id SET DEFAULT nextval('public.schedule_id_seq'::regclass);


--
-- Name: student_competitions id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.student_competitions ALTER COLUMN id SET DEFAULT nextval('public.student_competitions_id_seq'::regclass);


--
-- Name: students id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.students ALTER COLUMN id SET DEFAULT nextval('public.students_id_seq'::regclass);


--
-- Name: users id; Type: DEFAULT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- Data for Name: administration; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.administration (id, user_id, full_name, "position", contact_info) FROM stdin;
1	4	Олег Иванов	Директор	oleg@example.com
2	5	Наталья Смирнова	Менеджер	natalia@example.com
\.


--
-- Data for Name: coaches; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.coaches (id, user_id, full_name, specialization, contact_info) FROM stdin;
1	3	Алексей Смирнов	Бокс	alex.smirnov@example.com
2	4	Ольга Иванова	Легкая атлетика	olga.ivanova@example.com
3	5	ZZZ	аыва	fafae
4	7	sdfsd	sdfssdf	sdf
\.


--
-- Data for Name: competitions; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.competitions (id, name, event_date, location) FROM stdin;
1	Чемпионат города по боксу	2025-06-10 10:00:00	Спортзал №1
2	Легкоатлетический забег	2025-07-15 09:00:00	Стадион Олимп
\.


--
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.inventory (id, name, description, quantity, location) FROM stdin;
1	Перчатки боксерские	Кожаные, размер L	10	Склад 1
2	Шиповки	Размер 42	5	Склад 2
\.


--
-- Data for Name: inventory_movements; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.inventory_movements (id, inventory_id, student_id, coach_id, movement_type, destination, movement_date) FROM stdin;
1	1	19	1	issued	Зал 1	2025-03-14 00:25:45.310006+03
2	2	20	2	returned	Склад 2	2025-03-14 00:25:45.310006+03
3	1	19	1	issued	Зал1	2025-03-10
4	2	19	1	issued	Зал1	2025-03-23
5	1	19	1	issued	Зал1	2025-04-21
6	2	20	1	issued	Зал2	2025-04-21
\.


--
-- Data for Name: schedule; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.schedule (id, student_id, coach_id, class_date, location) FROM stdin;
1	19	1	2025-06-01 14:00:00	Зал 1
2	20	2	2025-06-02 15:00:00	Стадион
17	19	3	2025-04-21 08:00:00	Стадион
18	23	3	2025-04-25 14:00:00	Зал 1
19	23	2	2025-04-25 12:00:00	Зал 1
20	24	2	2025-04-19 16:00:00	Зал 1
21	22	3	2027-04-08 16:00:00	Зал 1
23	21	3	2025-04-23 12:00:00	Стадион
25	21	3	2025-04-21 08:00:00	Стадион
\.


--
-- Data for Name: student_competitions; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.student_competitions (id, student_id, competition_id, inventory_id) FROM stdin;
1	19	1	1
2	20	2	2
17	19	1	1
\.


--
-- Data for Name: students; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.students (id, user_id, full_name, birth_date, contact_info, registration_date, completed_lessons) FROM stdin;
19	1	Иван Петров	2008-05-10	ivan@example.com	2025-03-13 23:56:59.707108	0
20	2	Алексей Смирнов	2009-07-15	alexey@example.com	2025-03-13 23:56:59.707108	0
21	3	Мария Соколова	2007-09-20	maria@example.com	2025-03-13 23:56:59.707108	0
22	4	Екатерина Иванова	2010-02-25	ekaterina@example.com	2025-03-13 23:56:59.707108	0
23	5	Дмитрий Кузнецов	2006-12-05	dmitry@example.com	2025-03-13 23:56:59.707108	0
24	6	Анна Волкова	2008-11-30	anna@example.com	2025-03-13 23:56:59.707108	0
25	7	Николай Фёдоров	2009-04-18	nikolay@example.com	2025-03-13 23:56:59.707108	0
26	8	Ольга Медведева	2007-06-22	olga@example.com	2025-03-13 23:56:59.707108	0
\.


--
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: sportschool
--

COPY public.users (id, username, password_hash, role) FROM stdin;
2	administration	512afb6c763173d396baa0d08494e5845682df53d11f056110221a6601973e2c	administration
3	student	264c8c381bf16c982a4e59b0dd4c6f7808c51a05f64c35db42cc78a2a72875bb	student
4	coacher1	25fac00c0c3f81a9f9c7b38cbe2adc7b8fce2e422079ba0eb3bbf3f831c6cf48	coacher
7	admin1	25f43b1486ad95a1398e3eeb3d83bc4010015fcc9bedb35b432e00298d5021f7	administration
9	student1	509e87a6c45ee0a3c657bf946dd6dc43d7e5502143be195280f279002e70f7d9	student
5	coacher2	aa9349093649ff0ac8ab763ec11856a74367d1cfbafa749bada73802c31452f5	coacher
6	coacher3	1a2a489ab2d7504cf278315750c0ff2904e7e8b29c7f389a96b5893a4c8c229e	coacher
8	admin2	1c142b2d01aa34e9a36bde480645a57fd69e14155dacfab5a3f9257b77fdc8d8	administration
10	student2	eb4b3111401df980f14f28ad6804ae096df1e1c6963c51eab4140be226f8c94c	student
11	student3	373b29d2837e83b9ca5cec712a5985843df271cc7c06e64629472f4d03c6f83c	student
1	coacher	0c60b6f9a439e125e848ee76d82310a1d807334ab89a33ca5c9659fdf42c9268	coacher
\.


--
-- Name: administration_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.administration_id_seq', 5, true);


--
-- Name: coaches_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.coaches_id_seq', 6, true);


--
-- Name: competitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.competitions_id_seq', 3, true);


--
-- Name: inventory_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.inventory_id_seq', 4, true);


--
-- Name: inventory_movements_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.inventory_movements_id_seq', 7, true);


--
-- Name: schedule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.schedule_id_seq', 25, true);


--
-- Name: student_competitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.student_competitions_id_seq', 17, true);


--
-- Name: students_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.students_id_seq', 31, true);


--
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: sportschool
--

SELECT pg_catalog.setval('public.users_id_seq', 18, true);


--
-- Name: administration administration_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.administration
    ADD CONSTRAINT administration_pkey PRIMARY KEY (id);


--
-- Name: administration administration_user_id_key; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.administration
    ADD CONSTRAINT administration_user_id_key UNIQUE (user_id);


--
-- Name: coaches coaches_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.coaches
    ADD CONSTRAINT coaches_pkey PRIMARY KEY (id);


--
-- Name: coaches coaches_user_id_key; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.coaches
    ADD CONSTRAINT coaches_user_id_key UNIQUE (user_id);


--
-- Name: competitions competitions_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.competitions
    ADD CONSTRAINT competitions_pkey PRIMARY KEY (id);


--
-- Name: inventory_movements inventory_movements_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_pkey PRIMARY KEY (id);


--
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (id);


--
-- Name: schedule schedule_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_pkey PRIMARY KEY (id);


--
-- Name: student_competitions student_competitions_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.student_competitions
    ADD CONSTRAINT student_competitions_pkey PRIMARY KEY (id);


--
-- Name: students students_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_pkey PRIMARY KEY (id);


--
-- Name: students students_user_id_key; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_key UNIQUE (user_id);


--
-- Name: students unique_user; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT unique_user UNIQUE (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- Name: schedule check_self_coaching; Type: TRIGGER; Schema: public; Owner: sportschool
--

CREATE TRIGGER check_self_coaching BEFORE INSERT OR UPDATE ON public.schedule FOR EACH ROW EXECUTE FUNCTION public.prevent_self_coaching();


--
-- Name: administration administration_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.administration
    ADD CONSTRAINT administration_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: coaches coaches_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.coaches
    ADD CONSTRAINT coaches_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- Name: inventory_movements inventory_movements_coach_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_coach_id_fkey FOREIGN KEY (coach_id) REFERENCES public.coaches(id) ON DELETE SET NULL;


--
-- Name: inventory_movements inventory_movements_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventory(id) ON DELETE CASCADE;


--
-- Name: inventory_movements inventory_movements_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.inventory_movements
    ADD CONSTRAINT inventory_movements_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE SET NULL;


--
-- Name: schedule schedule_coach_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_coach_id_fkey FOREIGN KEY (coach_id) REFERENCES public.coaches(id) ON DELETE SET NULL;


--
-- Name: schedule schedule_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.schedule
    ADD CONSTRAINT schedule_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: student_competitions student_competitions_competition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.student_competitions
    ADD CONSTRAINT student_competitions_competition_id_fkey FOREIGN KEY (competition_id) REFERENCES public.competitions(id) ON DELETE CASCADE;


--
-- Name: student_competitions student_competitions_inventory_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.student_competitions
    ADD CONSTRAINT student_competitions_inventory_id_fkey FOREIGN KEY (inventory_id) REFERENCES public.inventory(id) ON DELETE SET NULL;


--
-- Name: student_competitions student_competitions_student_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.student_competitions
    ADD CONSTRAINT student_competitions_student_id_fkey FOREIGN KEY (student_id) REFERENCES public.students(id) ON DELETE CASCADE;


--
-- Name: students students_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: sportschool
--

ALTER TABLE ONLY public.students
    ADD CONSTRAINT students_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

