PGDMP     !                    z        
   tigerclimb    14.2    14.2     )           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            *           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            +           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            ,           1262    16395 
   tigerclimb    DATABASE     U   CREATE DATABASE tigerclimb WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'C';
    DROP DATABASE tigerclimb;
                postgres    false            �            1259    16408    comments    TABLE     �   CREATE TABLE public.comments (
    route_id integer NOT NULL,
    netid text NOT NULL,
    "timestamp" timestamp without time zone NOT NULL
);
    DROP TABLE public.comments;
       public         heap    postgres    false            �            1259    16469    grades    TABLE     j   CREATE TABLE public.grades (
    route_id integer NOT NULL,
    netid text,
    grade double precision
);
    DROP TABLE public.grades;
       public         heap    postgres    false            �            1259    16434    images    TABLE     �   CREATE TABLE public.images (
    filepath text NOT NULL,
    route_id integer NOT NULL,
    start_visible boolean,
    start_x integer,
    start_y integer
);
    DROP TABLE public.images;
       public         heap    postgres    false            �            1259    16448    profiles    TABLE     _   CREATE TABLE public.profiles (
    netid text NOT NULL,
    is_admin boolean,
    name text
);
    DROP TABLE public.profiles;
       public         heap    postgres    false            �            1259    16396    ratings    TABLE     Z   CREATE TABLE public.ratings (
    route_id integer,
    netid text,
    rating integer
);
    DROP TABLE public.ratings;
       public         heap    postgres    false            �            1259    16455    routes    TABLE       CREATE TABLE public.routes (
    route_id integer NOT NULL,
    name text,
    grade double precision,
    consensus_grade double precision,
    tape_col text,
    tape_col2 text,
    date_created date,
    descrip text,
    status text,
    rope integer,
    route_type text
);
    DROP TABLE public.routes;
       public         heap    postgres    false            �            1259    16441    rules    TABLE     �   CREATE TABLE public.rules (
    route_id integer NOT NULL,
    one_hold boolean,
    sit_start boolean,
    features boolean,
    rules text,
    is_default boolean
);
    DROP TABLE public.rules;
       public         heap    postgres    false            �            1259    16401    setters    TABLE     Y   CREATE TABLE public.setters (
    route_id integer NOT NULL,
    setter text NOT NULL
);
    DROP TABLE public.setters;
       public         heap    postgres    false            �            1259    16415    style    TABLE     V   CREATE TABLE public.style (
    route_id integer,
    netid text,
    keyword text
);
    DROP TABLE public.style;
       public         heap    postgres    false                       0    16408    comments 
   TABLE DATA           @   COPY public.comments (route_id, netid, "timestamp") FROM stdin;
    public          postgres    false    211   o       &          0    16469    grades 
   TABLE DATA           8   COPY public.grades (route_id, netid, grade) FROM stdin;
    public          postgres    false    217   �       "          0    16434    images 
   TABLE DATA           U   COPY public.images (filepath, route_id, start_visible, start_x, start_y) FROM stdin;
    public          postgres    false    213   �       $          0    16448    profiles 
   TABLE DATA           9   COPY public.profiles (netid, is_admin, name) FROM stdin;
    public          postgres    false    215   �                 0    16396    ratings 
   TABLE DATA           :   COPY public.ratings (route_id, netid, rating) FROM stdin;
    public          postgres    false    209   �       %          0    16455    routes 
   TABLE DATA           �   COPY public.routes (route_id, name, grade, consensus_grade, tape_col, tape_col2, date_created, descrip, status, rope, route_type) FROM stdin;
    public          postgres    false    216           #          0    16441    rules 
   TABLE DATA           [   COPY public.rules (route_id, one_hold, sit_start, features, rules, is_default) FROM stdin;
    public          postgres    false    214   �"                 0    16401    setters 
   TABLE DATA           3   COPY public.setters (route_id, setter) FROM stdin;
    public          postgres    false    210   �"       !          0    16415    style 
   TABLE DATA           9   COPY public.style (route_id, netid, keyword) FROM stdin;
    public          postgres    false    212   �"       �           2606    16414    comments comments_pkey 
   CONSTRAINT     n   ALTER TABLE ONLY public.comments
    ADD CONSTRAINT comments_pkey PRIMARY KEY (route_id, netid, "timestamp");
 @   ALTER TABLE ONLY public.comments DROP CONSTRAINT comments_pkey;
       public            postgres    false    211    211    211            �           2606    16475    grades grades_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.grades
    ADD CONSTRAINT grades_pkey PRIMARY KEY (route_id);
 <   ALTER TABLE ONLY public.grades DROP CONSTRAINT grades_pkey;
       public            postgres    false    217            �           2606    16440    images images_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.images
    ADD CONSTRAINT images_pkey PRIMARY KEY (route_id, filepath);
 <   ALTER TABLE ONLY public.images DROP CONSTRAINT images_pkey;
       public            postgres    false    213    213            �           2606    16454    profiles profiles_pkey 
   CONSTRAINT     W   ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (netid);
 @   ALTER TABLE ONLY public.profiles DROP CONSTRAINT profiles_pkey;
       public            postgres    false    215            �           2606    16461    routes routes_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.routes
    ADD CONSTRAINT routes_pkey PRIMARY KEY (route_id);
 <   ALTER TABLE ONLY public.routes DROP CONSTRAINT routes_pkey;
       public            postgres    false    216            �           2606    16447    rules rules_pkey 
   CONSTRAINT     T   ALTER TABLE ONLY public.rules
    ADD CONSTRAINT rules_pkey PRIMARY KEY (route_id);
 :   ALTER TABLE ONLY public.rules DROP CONSTRAINT rules_pkey;
       public            postgres    false    214            �           2606    16407    setters setters_pkey 
   CONSTRAINT     `   ALTER TABLE ONLY public.setters
    ADD CONSTRAINT setters_pkey PRIMARY KEY (route_id, setter);
 >   ALTER TABLE ONLY public.setters DROP CONSTRAINT setters_pkey;
       public            postgres    false    210    210                   x������ � �      &      x������ � �      "      x������ � �      $      x������ � �            x������ � �      %   �  x��W�r�F}E���9�q˛okR������Ծ�Q#�#e42˧��c���H�,`F~H��2����|6RC�����Ȃ�\��F�%�B?y~��=z�a�����=�Ϟ��vS�+�� 	c�2�w��l�B��C/�x�/d����p��ҫ�+���L�-pU�\��q��\W
�V�%��bCP���ȳ}�z^什��oE&ҕ�?�����*��%�?��� ���W����0�Y�}̠���,�PBW�L��^1]�b,ʐno�[^](�9�j-d
/��ԗm�t�9t ���7Xj��xB-$�h�kX|0H�=���f�T�Ds����BÜs �E
��{�4L	m�7�9X��<(�����4��!{�㘤�b鵛���D��K���"�d|��ӫr��Z<&��)���B�\-ڄ|pآ�@�EA���k߿�b�;#���>�U�*��F�e�;h������ށ(�!hD����9��r>d�埕Px��ℯ\��<R�Qð�Vd����
^�\�j�#oRv��*)��C�ӦU�e.k�ü���(	C�]Va�ʕ�`ɪ������P��?����J��S�u�����Z��>M�MY���X�1��5£$/S�]�dp&����W�\��'D��噞H��۲��Y&$u;��2�˜�x�i�|:�,�{Z��iŷ���>̒��7��N�^V�!U�/��N��˅I��m(��l�P����V�鄼���!����"�gȦeI��ӴE|_�s���CQf�9�I�}vg쨭���e���r�2�T��l�����{�R7�0E�S�R����ɑU&XJ��w��Z�=򮫉��^MJ��]F��ܔ�%d9��2��,sEG�e�ePP����`��~�u8�����ՒF*�ۧ�O��'��P$�Ƽ*�p�ם-�vOmйqZ��ǧ��;r�<���VeRR�}#�\�R^+���%f0Ϸt�3 �1������>��撎�d#7t��_y��AeVEq�&H/C��5��H�4rnL��؈���R�$s%��X�tY���#�BEi��������q�՝]��Y�F�-�D�[N_hz�x��;�\�~�v�o����霤��;�������:j�������_|y�      #      x������ � �            x�34261�,I-.�����  0{      !      x������ � �     