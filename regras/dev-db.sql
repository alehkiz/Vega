BEGIN TRANSACTION;
DROP TABLE IF EXISTS `user`;
CREATE TABLE IF NOT EXISTS `user` (
	`id`	INTEGER NOT NULL,
	`username`	VARCHAR ( 64 ) NOT NULL,
	`name`	VARCHAR ( 512 ) NOT NULL,
	`email`	VARCHAR ( 128 ) NOT NULL,
	`_password`	VARCHAR ( 512 ) NOT NULL,
	`about_me`	VARCHAR ( 512 ),
	`last_seen`	DATETIME,
	`location`	VARCHAR ( 128 ),
	`active`	BOOLEAN,
	`created_at`	DATETIME,
	`created_ip`	VARCHAR ( 255 ) NOT NULL,
	`last_login_at`	DATETIME,
	`last_login_ip`	VARCHAR ( 255 ),
	`current_login_at`	DATETIME,
	`current_login_ip`	VARCHAR ( 255 ),
	`confirmed_ip`	VARCHAR ( 255 ),
	`confirmed_at`	DATETIME,
	`login_count`	INTEGER,
	CHECK(activeIN(0,1)),
	PRIMARY KEY(`id`)
);
INSERT INTO `user` (id,username,name,email,_password,about_me,last_seen,location,active,created_at,created_ip,last_login_at,last_login_ip,current_login_at,current_login_ip,confirmed_ip,confirmed_at,login_count) VALUES (1,'admin','Administrador','Administrador','$pbkdf2-sha512$25000$EQLA2FtrTUkpJWQMwTgnZA$7dPcBx.S94rt9rRD4chtvbPxgna..sxBrjaETxgo3Dt.9T4/TOPS6AQ156RPPz9yx..Fcj6jXF9g935DQ4iDkA','asdsadadas','2021-01-20 04:13:08.393460',NULL,1,'2021-01-13 16:51:27.122036','0.0.0.0','2021-01-20 03:07:04.155970','127.0.0.1','2021-01-20 03:07:04.155970','127.0.0.1',NULL,NULL,46),
 (2,'alexandre','Alexandre Santos','alexandre@localhost','$pbkdf2-sha512$25000$9t57zxmDEKIUYozx3ntv7Q$5YqBvE.aUTMYs8JegFogTYXV9HMiqJRksXiE6o0pcq6Mmo6QQPUGss2hO5JOT8ZzoUydkf1hTAHWY1ObsB2LQA',NULL,'2021-01-20 03:06:58.263626',NULL,1,'2021-01-17 17:21:27.123020','0.0.0.0','2021-01-20 03:05:02.448936','127.0.0.1','2021-01-20 03:05:02.448936','127.0.0.1',NULL,NULL,6);
DROP TABLE IF EXISTS `topic`;
CREATE TABLE IF NOT EXISTS `topic` (
	`id`	INTEGER NOT NULL,
	`_name`	VARCHAR ( 32 ) NOT NULL,
	`formated_name`	VARCHAR ( 32 ),
	`timestamp`	DATETIME,
	PRIMARY KEY(`id`)
);
INSERT INTO `topic` (id,_name,formated_name,timestamp) VALUES (1,'Topico 1','topico_1','2021-01-17 21:32:33.454647'),
 (2,'Tópico 2 - o teste','topico_2__o_teste','2021-01-17 21:42:27.799807');
DROP TABLE IF EXISTS `tag`;
CREATE TABLE IF NOT EXISTS `tag` (
	`id`	INTEGER NOT NULL,
	`name`	VARCHAR ( 48 ) NOT NULL,
	`timestamp`	DATETIME,
	`user_id`	INTEGER,
	PRIMARY KEY(`id`),
	FOREIGN KEY(`user_id`) REFERENCES `user`(`id`)
);
INSERT INTO `tag` (id,name,timestamp,user_id) VALUES (1,'Testing','2021-01-14 20:56:40.228827',NULL);
DROP TABLE IF EXISTS `roles_users`;
CREATE TABLE IF NOT EXISTS `roles_users` (
	`user_id`	INTEGER,
	`role_id`	INTEGER,
	FOREIGN KEY(`user_id`) REFERENCES `user`(`id`),
	FOREIGN KEY(`role_id`) REFERENCES `role`(`id`)
);
INSERT INTO `roles_users` (user_id,role_id) VALUES (1,1),
 (2,3);
DROP TABLE IF EXISTS `role`;
CREATE TABLE IF NOT EXISTS `role` (
	`id`	INTEGER NOT NULL,
	`level`	INTEGER NOT NULL,
	`name`	VARCHAR ( 128 ) NOT NULL UNIQUE,
	`description`	VARCHAR ( 255 ),
	PRIMARY KEY(`id`)
);
INSERT INTO `role` (id,level,name,description) VALUES (1,0,'admin','Adminitrador'),
 (2,1,'manager_user','Gerenciador de Usuários'),
 (3,2,'editor','Gerenciador de Conteúdo'),
 (4,3,'aux_editor','Editor Auxiliar'),
 (5,4,'viewer','Visulizador');
DROP TABLE IF EXISTS `article_view`;
CREATE TABLE IF NOT EXISTS `article_view` (
	`id`	INTEGER NOT NULL,
	`count_view`	INTEGER,
	`first_view`	DATETIME,
	`last_view`	DATETIME,
	`user_id`	INTEGER,
	`article_id`	INTEGER NOT NULL,
	FOREIGN KEY(`user_id`) REFERENCES `user`(`id`),
	PRIMARY KEY(`id`),
	FOREIGN KEY(`article_id`) REFERENCES `article`(`id`)
);
INSERT INTO `article_view` (id,count_view,first_view,last_view,user_id,article_id) VALUES (1,155,'2021-01-17 16:12:22.720118','2021-01-20 03:07:28.034599',1,1),
 (2,21,'2021-01-17 16:31:34.228960','2021-01-18 23:28:03.532846',NULL,1),
 (3,2,'2021-01-17 17:07:57.522069','2021-01-17 17:08:50.094928',1,2),
 (4,2,'2021-01-17 17:07:58.109676','2021-01-17 21:53:48.493574',1,3),
 (5,1,'2021-01-17 17:07:58.619368','2021-01-17 17:07:58.619368',1,4),
 (6,3,'2021-01-17 17:07:59.878642','2021-01-20 01:21:33.867060',1,5),
 (7,74,'2021-01-17 17:08:13.031820','2021-01-20 03:38:13.062571',1,6),
 (8,151,'2021-01-17 17:21:59.356083','2021-01-17 20:47:51.683164',2,1),
 (9,8,'2021-01-17 20:45:16.413953','2021-01-17 20:45:26.646746',2,3),
 (10,1,'2021-01-20 02:08:42.581630','2021-01-20 02:08:42.581630',NULL,6),
 (11,1,'2021-01-20 03:06:51.186408','2021-01-20 03:06:51.186408',2,6);
DROP TABLE IF EXISTS `article_tag`;
CREATE TABLE IF NOT EXISTS `article_tag` (
	`post_id`	INTEGER,
	`tag_id`	INTEGER,
	FOREIGN KEY(`post_id`) REFERENCES `article`(`id`),
	FOREIGN KEY(`tag_id`) REFERENCES `tag`(`id`)
);
INSERT INTO `article_tag` (post_id,tag_id) VALUES (1,1);
DROP TABLE IF EXISTS `article`;
CREATE TABLE IF NOT EXISTS `article` (
	`id`	INTEGER NOT NULL,
	`title`	VARCHAR ( 32 ) NOT NULL,
	`description`	VARCHAR ( 128 ) NOT NULL,
	`_text`	TEXT NOT NULL,
	`timestamp`	DATETIME,
	`user_id`	INTEGER,
	`topic_id`	INTEGER,
	`updated_timestamp`	DATETIME,
	`updated_user_id`	INTEGER,
	FOREIGN KEY(`user_id`) REFERENCES `user`(`id`),
	FOREIGN KEY(`topic_id`) REFERENCES `topic`(`id`),
	FOREIGN KEY(`updated_user_id`) REFERENCES `user`(`id`),
	PRIMARY KEY(`id`)
);
INSERT INTO `article` (id,title,description,_text,timestamp,user_id,topic_id,updated_timestamp,updated_user_id) VALUES (1,'teste','teste decrição','**Table of Contents**

[TOCM]

[TOC]

#H1 header
##H2 header
###H3 header
####H4 header
#####H5 header
######H6 header
#Heading 1 link [Heading link](https://github.com/pandao/editor.md "Heading link")
##Heading 2 link [Heading link](https://github.com/pandao/editor.md "Heading link")
###Heading 3 link [Heading link](https://github.com/pandao/editor.md "Heading link")
####Heading 4 link [Heading link](https://github.com/pandao/editor.md "Heading link") Heading link [Heading link](https://github.com/pandao/editor.md "Heading link")
#####Heading 5 link [Heading link](https://github.com/pandao/editor.md "Heading link")
######Heading 6 link [Heading link](https://github.com/pandao/editor.md "Heading link")

##Headers (Underline)

H1 Header (Underline)
=============

H2 Header (Underline)
-------------

###Characters
                
----

~~Strikethrough~~ Strikethrough (when enable html tag decode.)
*Italic*      _Italic_
**Emphasis**  __Emphasis__
***Emphasis Italic*** ___Emphasis Italic___

Superscript: X2，Subscript: O2

**Abbreviation(link HTML abbr tag)**

The HTML specification is maintained by the W3C.

###Blockquotes

> Blockquotes

Paragraphs and Line Breaks
                    
> "Blockquotes Blockquotes", [Link](http://localhost/)。','2021-01-14 20:53:57.801403',1,1,'2021-01-20 03:07:27.894218',1),
 (2,'Text about python','Esse é um texto sobre python explicando filters e etc...','# **History**

Alonzo Church formalized lambda calculus, a language based on pure abstraction, in the 1930s. Lambda functions are also referred to as lambda abstractions, a direct reference to the abstraction model of Alonzo Church’s original creation.

Lambda calculus can encode any computation. It is Turing complete, but contrary to the concept of a Turing machine, it is pure and does not keep any state.

Functional languages get their origin in mathematical logic and lambda calculus, while imperative programming languages embrace the state-based model of computation invented by Alan Turing. The two models of computation, lambda calculus and Turing machines, can be translated into each another. This equivalence is known as the Church-Turing hypothesis.

Functional languages directly inherit the lambda calculus philosophy, adopting a declarative approach of programming that emphasizes abstraction, data transformation, composition, and purity (no state and no side effects). Examples of functional languages include Haskell, Lisp, or Erlang.

By contrast, the Turing Machine led to imperative programming found in languages like Fortran, C, or Python.

The imperative style consists of programming with statements, driving the flow of the program step by step with detailed instructions. This approach promotes mutation and requires managing state.

The separation in both families presents some nuances, as some functional languages incorporate imperative features, like OCaml, while functional features have been permeating the imperative family of languages in particular with the introduction of lambda functions in Java, or Python.

Python is not inherently a functional language, but it adopted some functional concepts early on. In January 1994, map(), filter(), reduce(), and the lambda operator were added to the language.
First Example

Here are a few examples to give you an appetite for some Python code, functional style.

The identity function, a function that returns its argument, is expressed with a standard Python function definition using the keyword def as follows:

>>> def identity(x):
...     return x

identity() takes an argument x and returns it upon invocation.

In contrast, if you use a Python lambda construction, you get the following:

>>> lambda x: x

In the example above, the expression is composed of:

    The keyword: lambda
    A bound variable: x
    A body: x

Note: In the context of this article, a bound variable is an argument to a lambda function.

In contrast, a free variable is not bound and may be referenced in the body of the expression. A free variable can be a constant or a variable defined in the enclosing scope of the function.

You can write a slightly more elaborated example, a function that adds 1 to an argument, as follows:

>>> lambda x: x + 1

You can apply the function above to an argument by surrounding the function and its argument with parentheses:

>>> (lambda x: x + 1)(2)
3

Reduction is a lambda calculus strategy to compute the value of the expression. In the current example, it consists of replacing the bound variable x with the argument 2:

(lambda x: x + 1)(2) = lambda 2: 2 + 1
                     = 2 + 1
                     = 3

Because a lambda function is an expression, it can be named. Therefore you could write the previous code as follows:

>>> add_one = lambda x: x + 1
>>> add_one(2)
3

The above lambda function is equivalent to writing this:

def add_one(x):
    return x + 1

These functions all take a single argument. You may have noticed that, in the definition of the lambdas, the arguments don’t have parentheses around them. Multi-argument functions (functions that take more than one argument) are expressed in Python lambdas by listing arguments and separating them with a comma (,) but without surrounding them with parentheses:

>>> full_name = lambda first, last: f''Full name: {first.title()} {last.title()}''
>>> full_name(''guido'', ''van rossum'')
''Full name: Guido Van Rossum''

The lambda function assigned to full_name takes two arguments and returns a string interpolating the two parameters first and last. As expected, the definition of the lambda lists the arguments with no parentheses, whereas calling the function is done exactly like a normal Python function, with parentheses surrounding the arguments.
Remove ads
Anonymous Functions

The following terms may be used interchangeably depending on the programming language type and culture:

    Anonymous functions
    Lambda functions
    Lambda expressions
    Lambda abstractions
    Lambda form
    Function literals

For the rest of this article after this section, you’ll mostly see the term lambda function.

Taken literally, an anonymous function is a function without a name. In Python, an anonymous function is created with the lambda keyword. More loosely, it may or not be assigned a name. Consider a two-argument anonymous function defined with lambda but not bound to a variable. The lambda is not given a name:

>>> lambda x, y: x + y

The function above defines a lambda expression that takes two arguments and returns their sum.

Other than providing you with the feedback that Python is perfectly fine with this form, it doesn’t lead to any practical use. You could invoke the function in the Python interpreter:

>>> _(1, 2)
3

The example above is taking advantage of the interactive interpreter-only feature provided via the underscore (_). See the note below for more details.

You could not write similar code in a Python module. Consider the _ in the interpreter as a side effect that you took advantage of. In a Python module, you would assign a name to the lambda, or you would pass the lambda to a function. You’ll use those two approaches later in this article.

Note: In the interactive interpreter, the single underscore (_) is bound to the last expression evaluated.

In the example above, the _ points to the lambda function. For more details about the usage of this special character in Python, check out The Meaning of Underscores in Python.

Another pattern used in other languages like JavaScript is to immediately execute a Python lambda function. This is known as an Immediately Invoked Function Expression (IIFE, pronounce “iffy”). Here’s an example:

>>> (lambda x, y: x + y)(2, 3)
5

The lambda function above is defined and then immediately called with two arguments (2 and 3). It returns the value 5, which is the sum of the arguments.

Several examples in this tutorial use this format to highlight the anonymous aspect of a lambda function and avoid focusing on lambda in Python as a shorter way of defining a function.

Python does not encourage using immediately invoked lambda expressions. It simply results from a lambda expression being callable, unlike the body of a normal function.

Lambda functions are frequently used with higher-order functions, which take one or more functions as arguments or return one or more functions.

A lambda function can be a higher-order function by taking a function (normal or lambda) as an argument like in the following contrived example:

>>> high_ord_func = lambda x, func: x + func(x)
>>> high_ord_func(2, lambda x: x * x)
6
>>> high_ord_func(2, lambda x: x + 3)
7

Python exposes higher-order functions as built-in functions or in the standard library. Examples include map(), filter(), functools.reduce(), as well as key functions like sort(), sorted(), min(), and max(). You’ll use lambda functions together with Python higher-order functions in Appropriate Uses of Lambda Expressions.
Remove ads
Python Lambda and Regular Functions

This quote from the Python Design and History FAQ seems to set the tone about the overall expectation regarding the usage of lambda functions in Python:

    Unlike lambda forms in other languages, where they add functionality, Python lambdas are only a shorthand notation if you’re too lazy to define a function. (Source)

Nevertheless, don’t let this statement deter you from using Python’s lambda. At first glance, you may accept that a lambda function is a function with some syntactic sugar shortening the code to define or invoke a function. The following sections highlight the commonalities and subtle differences between normal Python functions and lambda functions.
Functions

At this point, you may wonder what fundamentally distinguishes a lambda function bound to a variable from a regular function with a single return line: under the surface, almost nothing. Let’s verify how Python sees a function built with a single return statement versus a function constructed as an expression (lambda).

The dis module exposes functions to analyze Python bytecode generated by the Python compiler:

```python
import dis
add = lambda x, y: x + y
type(add)
<class ''function''>
dis.dis(add)
  1           0 LOAD_FAST                0 (x)
              2 LOAD_FAST                1 (y)
              4 BINARY_ADD
              6 RETURN_VALUE
add
<function <lambda> at 0x7f30c6ce9ea0>
```

You can see that dis() expose a readable version of the Python bytecode allowing the inspection of the low-level instructions that the Python interpreter will use while executing the program.

Now see it with a regular function object:

>>> import dis
>>> def add(x, y): return x + y
>>> type(add)
<class ''function''>
>>> dis.dis(add)
  1           0 LOAD_FAST                0 (x)
              2 LOAD_FAST                1 (y)
              4 BINARY_ADD
              6 RETURN_VALUE
>>> add
<function add at 0x7f30c6ce9f28>

The bytecode interpreted by Python is the same for both functions. But you may notice that the naming is different: the function name is add for a function defined with def, whereas the Python lambda function is seen as lambda.
Traceback

You saw in the previous section that, in the context of the lambda function, Python did not provide the name of the function, but only <lambda>. This can be a limitation to consider when an exception occurs, and a traceback shows only <lambda>:

>>> div_zero = lambda x: x / 0
>>> div_zero(2)
Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "<stdin>", line 1, in <lambda>
ZeroDivisionError: division by zero

The traceback of an exception raised while a lambda function is executed only identifies the function causing the exception as <lambda>.

Here’s the same exception raised by a normal function:

>>> def div_zero(x): return x / 0
>>> div_zero(2)
Traceback (most recent call last):
    File "<stdin>", line 1, in <module>
    File "<stdin>", line 1, in div_zero
ZeroDivisionError: division by zero

The normal function causes a similar error but results in a more precise traceback because it gives the function name, div_zero.
Syntax

As you saw in the previous sections, a lambda form presents syntactic distinctions from a normal function. In particular, a lambda function has the following characteristics:

    It can only contain expressions and can’t include statements in its body.
    It is written as a single line of execution.
    It does not support type annotations.
    It can be immediately invoked (IIFE).

No Statements

A lambda function can’t contain any statements. In a lambda function, statements like return, pass, assert, or raise will raise a SyntaxError exception. Here’s an example of adding assert to the body of a lambda:

>>> (lambda x: assert x == 2)(2)
  File "<input>", line 1
    (lambda x: assert x == 2)(2)
                    ^
SyntaxError: invalid syntax

This contrived example intended to assert that parameter x had a value of 2. But, the interpreter identifies a SyntaxError while parsing the code that involves the statement assert in the body of the lambda.

Single Expression

In contrast to a normal function, a Python lambda function is a single expression. Although, in the body of a lambda, you can spread the expression over several lines using parentheses or a multiline string, it remains a single expression:

>>> (lambda x:
... (x % 2 and ''odd'' or ''even''))(3)
''odd''

The example above returns the string ''odd'' when the lambda argument is odd, and ''even'' when the argument is even. It spreads across two lines because it is contained in a set of parentheses, but it remains a single expression.

Type Annotations

If you’ve started adopting type hinting, which is now available in Python, then you have another good reason to prefer normal functions over Python lambda functions. Check out Python Type Checking (Guide) to get learn more about Python type hints and type checking. In a lambda function, there is no equivalent for the following:','2021-01-15 17:19:12.389503',2,1,NULL,NULL),
 (3,'outro texto python','Explicando python','# **History** Alonzo Church formalized lambda calculus, a language based on pure abstraction, in the 1930s. Lambda functions are also referred to as lambda abstractions, a direct reference to the abstraction model of Alonzo Church’s original creation. Lambda calculus can encode any computation. It is Turing complete, but contrary to the concept of a Turing machine, it is pure and does not keep any state. Functional languages get their origin in mathematical logic and lambda calculus, while imperative programming languages embrace the state-based model of computation invented by Alan Turing. The two models of computation, lambda calculus and Turing machines, can be translated into each another. This equivalence is known as the Church-Turing hypothesis. Functional languages directly inherit the lambda calculus philosophy, adopting a declarative approach of programming that emphasizes abstraction, data transformation, composition, and purity (no state and no side effects). Examples of functional languages include Haskell, Lisp, or Erlang. By contrast, the Turing Machine led to imperative programming found in languages like Fortran, C, or Python. The imperative style consists of programming with statements, driving the flow of the program step by step with detailed instructions. This approach promotes mutation and requires managing state. The separation in both families presents some nuances, as some functional languages incorporate imperative features, like OCaml, while functional features have been permeating the imperative family of languages in particular with the introduction of lambda functions in Java, or Python. Python is not inherently a functional language, but it adopted some functional concepts early on. In January 1994, map(), filter(), reduce(), and the lambda operator were added to the language. First Example Here are a few examples to give you an appetite for some Python code, functional style. The identity function, a function that returns its argument, is expressed with a standard Python function definition using the keyword def as follows: >>> def identity(x): ... return x identity() takes an argument x and returns it upon invocation. In contrast, if you use a Python lambda construction, you get the following: >>> lambda x: x In the example above, the expression is composed of: The keyword: lambda A bound variable: x A body: x Note: In the context of this article, a bound variable is an argument to a lambda function. In contrast, a free variable is not bound and may be referenced in the body of the expression. A free variable can be a constant or a variable defined in the enclosing scope of the function. You can write a slightly more elaborated example, a function that adds 1 to an argument, as follows: >>> lambda x: x + 1 You can apply the function above to an argument by surrounding the function and its argument with parentheses: >>> (lambda x: x + 1)(2) 3 Reduction is a lambda calculus strategy to compute the value of the expression. In the current example, it consists of replacing the bound variable x with the argument 2: (lambda x: x + 1)(2) = lambda 2: 2 + 1 = 2 + 1 = 3 Because a lambda function is an expression, it can be named. Therefore you could write the previous code as follows: >>> add_one = lambda x: x + 1 >>> add_one(2) 3 The above lambda function is equivalent to writing this: def add_one(x): return x + 1 These functions all take a single argument. You may have noticed that, in the definition of the lambdas, the arguments don’t have parentheses around them. Multi-argument functions (functions that take more than one argument) are expressed in Python lambdas by listing arguments and separating them with a comma (,) but without surrounding them with parentheses: >>> full_name = lambda first, last: f''Full name: {first.title()} {last.title()}'' >>> full_name(''guido'', ''van rossum'') ''Full name: Guido Van Rossum'' The lambda function assigned to full_name takes two arguments and returns a string interpolating the two parameters first and last. As expected, the definition of the lambda lists the arguments with no parentheses, whereas calling the function is done exactly like a normal Python function, with parentheses surrounding the arguments. Remove ads Anonymous Functions The following terms may be used interchangeably depending on the programming language type and culture: Anonymous functions Lambda functions Lambda expressions Lambda abstractions Lambda form Function literals For the rest of this article after this section, you’ll mostly see the term lambda function. Taken literally, an anonymous function is a function without a name. In Python, an anonymous function is created with the lambda keyword. More loosely, it may or not be assigned a name. Consider a two-argument anonymous function defined with lambda but not bound to a variable. The lambda is not given a name: >>> lambda x, y: x + y The function above defines a lambda expression that takes two arguments and returns their sum. Other than providing you with the feedback that Python is perfectly fine with this form, it doesn’t lead to any practical use. You could invoke the function in the Python interpreter: >>> _(1, 2) 3 The example above is taking advantage of the interactive interpreter-only feature provided via the underscore (_). See the note below for more details. You could not write similar code in a Python module. Consider the _ in the interpreter as a side effect that you took advantage of. In a Python module, you would assign a name to the lambda, or you would pass the lambda to a function. You’ll use those two approaches later in this article. Note: In the interactive interpreter, the single underscore (_) is bound to the last expression evaluated. In the example above, the _ points to the lambda function. For more details about the usage of this special character in Python, check out The Meaning of Underscores in Python. Another pattern used in other languages like JavaScript is to immediately execute a Python lambda function. This is known as an Immediately Invoked Function Expression (IIFE, pronounce “iffy”). Here’s an example: >>> (lambda x, y: x + y)(2, 3) 5 The lambda function above is defined and then immediately called with two arguments (2 and 3). It returns the value 5, which is the sum of the arguments. Several examples in this tutorial use this format to highlight the anonymous aspect of a lambda function and avoid focusing on lambda in Python as a shorter way of defining a function. Python does not encourage using immediately invoked lambda expressions. It simply results from a lambda expression being callable, unlike the body of a normal function. Lambda functions are frequently used with higher-order functions, which take one or more functions as arguments or return one or more functions. A lambda function can be a higher-order function by taking a function (normal or lambda) as an argument like in the following contrived example: >>> high_ord_func = lambda x, func: x + func(x) >>> high_ord_func(2, lambda x: x * x) 6 >>> high_ord_func(2, lambda x: x + 3) 7 Python exposes higher-order functions as built-in functions or in the standard library. Examples include map(), filter(), functools.reduce(), as well as key functions like sort(), sorted(), min(), and max(). You’ll use lambda functions together with Python higher-order functions in Appropriate Uses of Lambda Expressions. Remove ads Python Lambda and Regular Functions This quote from the Python Design and History FAQ seems to set the tone about the overall expectation regarding the usage of lambda functions in Python: Unlike lambda forms in other languages, where they add functionality, Python lambdas are only a shorthand notation if you’re too lazy to define a function. (Source) Nevertheless, don’t let this statement deter you from using Python’s lambda. At first glance, you may accept that a lambda function is a function with some syntactic sugar shortening the code to define or invoke a function. The following sections highlight the commonalities and subtle differences between normal Python functions and lambda functions. Functions At this point, you may wonder what fundamentally distinguishes a lambda function bound to a variable from a regular function with a single return line: under the surface, almost nothing. Let’s verify how Python sees a function built with a single return statement versus a function constructed as an expression (lambda). The dis module exposes functions to analyze Python bytecode generated by the Python compiler: ```python import dis add = lambda x, y: x + y type(add) dis.dis(add) 1 0 LOAD_FAST 0 (x) 2 LOAD_FAST 1 (y) 4 BINARY_ADD 6 RETURN_VALUE add at 0x7f30c6ce9ea0> ``` You can see that dis() expose a readable version of the Python bytecode allowing the inspection of the low-level instructions that the Python interpreter will use while executing the program. Now see it with a regular function object: >>> import dis >>> def add(x, y): return x + y >>> type(add) >>> dis.dis(add) 1 0 LOAD_FAST 0 (x) 2 LOAD_FAST 1 (y) 4 BINARY_ADD 6 RETURN_VALUE >>> add The bytecode interpreted by Python is the same for both functions. But you may notice that the naming is different: the function name is add for a function defined with def, whereas the Python lambda function is seen as lambda. Traceback You saw in the previous section that, in the context of the lambda function, Python did not provide the name of the function, but only . This can be a limitation to consider when an exception occurs, and a traceback shows only : >>> div_zero = lambda x: x / 0 >>> div_zero(2) Traceback (most recent call last): File "", line 1, in File "", line 1, in ZeroDivisionError: division by zero The traceback of an exception raised while a lambda function is executed only identifies the function causing the exception as . Here’s the same exception raised by a normal function: >>> def div_zero(x): return x / 0 >>> div_zero(2) Traceback (most recent call last): File "", line 1, in File "", line 1, in div_zero ZeroDivisionError: division by zero The normal function causes a similar error but results in a more precise traceback because it gives the function name, div_zero. Syntax As you saw in the previous sections, a lambda form presents syntactic distinctions from a normal function. In particular, a lambda function has the following characteristics: It can only contain expressions and can’t include statements in its body. It is written as a single line of execution. It does not support type annotations. It can be immediately invoked (IIFE). No Statements A lambda function can’t contain any statements. In a lambda function, statements like return, pass, assert, or raise will raise a SyntaxError exception. Here’s an example of adding assert to the body of a lambda: >>> (lambda x: assert x == 2)(2) File "", line 1 (lambda x: assert x == 2)(2) ^ SyntaxError: invalid syntax This contrived example intended to assert that parameter x had a value of 2. But, the interpreter identifies a SyntaxError while parsing the code that involves the statement assert in the body of the lambda. Single Expression In contrast to a normal function, a Python lambda function is a single expression. Although, in the body of a lambda, you can spread the expression over several lines using parentheses or a multiline string, it remains a single expression: >>> (lambda x: ... (x % 2 and ''odd'' or ''even''))(3) ''odd'' The example above returns the string ''odd'' when the lambda argument is odd, and ''even'' when the argument is even. It spreads across two lines because it is contained in a set of parentheses, but it remains a single expression. Type Annotations If you’ve started adopting type hinting, which is now available in Python, then you have another good reason to prefer normal functions over Python lambda functions. Check out Python Type Checking (Guide) to get learn more about Python type hints and type checking. In a lambda function, there is no equivalent for the following:','2021-01-15 17:36:31.928375',1,2,NULL,NULL),
 (4,'outro texto python2','Explicando python','# **History** Alonzo Church formalized lambda calculus, a language based on pure abstraction, in the 1930s. Lambda functions are also referred to as lambda abstractions, a direct reference to the abstraction model of Alonzo Church’s original creation. Lambda calculus can encode any computation. It is Turing complete, but contrary to the concept of a Turing machine, it is pure and does not keep any state. Functional languages get their origin in mathematical logic and lambda calculus, while imperative programming languages embrace the state-based model of computation invented by Alan Turing. The two models of computation, lambda calculus and Turing machines, can be translated into each another. This equivalence is known as the Church-Turing hypothesis. Functional languages directly inherit the lambda calculus philosophy, adopting a declarative approach of programming that emphasizes abstraction, data transformation, composition, and purity (no state and no side effects). Examples of functional languages include Haskell, Lisp, or Erlang. By contrast, the Turing Machine led to imperative programming found in languages like Fortran, C, or Python. The imperative style consists of programming with statements, driving the flow of the program step by step with detailed instructions. This approach promotes mutation and requires managing state. The separation in both families presents some nuances, as some functional languages incorporate imperative features, like OCaml, while functional features have been permeating the imperative family of languages in particular with the introduction of lambda functions in Java, or Python. Python is not inherently a functional language, but it adopted some functional concepts early on. In January 1994, map(), filter(), reduce(), and the lambda operator were added to the language. First Example Here are a few examples to give you an appetite for some Python code, functional style. The identity function, a function that returns its argument, is expressed with a standard Python function definition using the keyword def as follows: >>> def identity(x): ... return x identity() takes an argument x and returns it upon invocation. In contrast, if you use a Python lambda construction, you get the following: >>> lambda x: x In the example above, the expression is composed of: The keyword: lambda A bound variable: x A body: x Note: In the context of this article, a bound variable is an argument to a lambda function. In contrast, a free variable is not bound and may be referenced in the body of the expression. A free variable can be a constant or a variable defined in the enclosing scope of the function. You can write a slightly more elaborated example, a function that adds 1 to an argument, as follows: >>> lambda x: x + 1 You can apply the function above to an argument by surrounding the function and its argument with parentheses: >>> (lambda x: x + 1)(2) 3 Reduction is a lambda calculus strategy to compute the value of the expression. In the current example, it consists of replacing the bound variable x with the argument 2: (lambda x: x + 1)(2) = lambda 2: 2 + 1 = 2 + 1 = 3 Because a lambda function is an expression, it can be named. Therefore you could write the previous code as follows: >>> add_one = lambda x: x + 1 >>> add_one(2) 3 The above lambda function is equivalent to writing this: def add_one(x): return x + 1 These functions all take a single argument. You may have noticed that, in the definition of the lambdas, the arguments don’t have parentheses around them. Multi-argument functions (functions that take more than one argument) are expressed in Python lambdas by listing arguments and separating them with a comma (,) but without surrounding them with parentheses: >>> full_name = lambda first, last: f''Full name: {first.title()} {last.title()}'' >>> full_name(''guido'', ''van rossum'') ''Full name: Guido Van Rossum'' The lambda function assigned to full_name takes two arguments and returns a string interpolating the two parameters first and last. As expected, the definition of the lambda lists the arguments with no parentheses, whereas calling the function is done exactly like a normal Python function, with parentheses surrounding the arguments. Remove ads Anonymous Functions The following terms may be used interchangeably depending on the programming language type and culture: Anonymous functions Lambda functions Lambda expressions Lambda abstractions Lambda form Function literals For the rest of this article after this section, you’ll mostly see the term lambda function. Taken literally, an anonymous function is a function without a name. In Python, an anonymous function is created with the lambda keyword. More loosely, it may or not be assigned a name. Consider a two-argument anonymous function defined with lambda but not bound to a variable. The lambda is not given a name: >>> lambda x, y: x + y The function above defines a lambda expression that takes two arguments and returns their sum. Other than providing you with the feedback that Python is perfectly fine with this form, it doesn’t lead to any practical use. You could invoke the function in the Python interpreter: >>> _(1, 2) 3 The example above is taking advantage of the interactive interpreter-only feature provided via the underscore (_). See the note below for more details. You could not write similar code in a Python module. Consider the _ in the interpreter as a side effect that you took advantage of. In a Python module, you would assign a name to the lambda, or you would pass the lambda to a function. You’ll use those two approaches later in this article. Note: In the interactive interpreter, the single underscore (_) is bound to the last expression evaluated. In the example above, the _ points to the lambda function. For more details about the usage of this special character in Python, check out The Meaning of Underscores in Python. Another pattern used in other languages like JavaScript is to immediately execute a Python lambda function. This is known as an Immediately Invoked Function Expression (IIFE, pronounce “iffy”). Here’s an example: >>> (lambda x, y: x + y)(2, 3) 5 The lambda function above is defined and then immediately called with two arguments (2 and 3). It returns the value 5, which is the sum of the arguments. Several examples in this tutorial use this format to highlight the anonymous aspect of a lambda function and avoid focusing on lambda in Python as a shorter way of defining a function. Python does not encourage using immediately invoked lambda expressions. It simply results from a lambda expression being callable, unlike the body of a normal function. Lambda functions are frequently used with higher-order functions, which take one or more functions as arguments or return one or more functions. A lambda function can be a higher-order function by taking a function (normal or lambda) as an argument like in the following contrived example: >>> high_ord_func = lambda x, func: x + func(x) >>> high_ord_func(2, lambda x: x * x) 6 >>> high_ord_func(2, lambda x: x + 3) 7 Python exposes higher-order functions as built-in functions or in the standard library. Examples include map(), filter(), functools.reduce(), as well as key functions like sort(), sorted(), min(), and max(). You’ll use lambda functions together with Python higher-order functions in Appropriate Uses of Lambda Expressions. Remove ads Python Lambda and Regular Functions This quote from the Python Design and History FAQ seems to set the tone about the overall expectation regarding the usage of lambda functions in Python: Unlike lambda forms in other languages, where they add functionality, Python lambdas are only a shorthand notation if you’re too lazy to define a function. (Source) Nevertheless, don’t let this statement deter you from using Python’s lambda. At first glance, you may accept that a lambda function is a function with some syntactic sugar shortening the code to define or invoke a function. The following sections highlight the commonalities and subtle differences between normal Python functions and lambda functions. Functions At this point, you may wonder what fundamentally distinguishes a lambda function bound to a variable from a regular function with a single return line: under the surface, almost nothing. Let’s verify how Python sees a function built with a single return statement versus a function constructed as an expression (lambda). The dis module exposes functions to analyze Python bytecode generated by the Python compiler: ```python import dis add = lambda x, y: x + y type(add) dis.dis(add) 1 0 LOAD_FAST 0 (x) 2 LOAD_FAST 1 (y) 4 BINARY_ADD 6 RETURN_VALUE add at 0x7f30c6ce9ea0> ``` You can see that dis() expose a readable version of the Python bytecode allowing the inspection of the low-level instructions that the Python interpreter will use while executing the program. Now see it with a regular function object: >>> import dis >>> def add(x, y): return x + y >>> type(add) >>> dis.dis(add) 1 0 LOAD_FAST 0 (x) 2 LOAD_FAST 1 (y) 4 BINARY_ADD 6 RETURN_VALUE >>> add The bytecode interpreted by Python is the same for both functions. But you may notice that the naming is different: the function name is add for a function defined with def, whereas the Python lambda function is seen as lambda. Traceback You saw in the previous section that, in the context of the lambda function, Python did not provide the name of the function, but only . This can be a limitation to consider when an exception occurs, and a traceback shows only : >>> div_zero = lambda x: x / 0 >>> div_zero(2) Traceback (most recent call last): File "", line 1, in File "", line 1, in ZeroDivisionError: division by zero The traceback of an exception raised while a lambda function is executed only identifies the function causing the exception as . Here’s the same exception raised by a normal function: >>> def div_zero(x): return x / 0 >>> div_zero(2) Traceback (most recent call last): File "", line 1, in File "", line 1, in div_zero ZeroDivisionError: division by zero The normal function causes a similar error but results in a more precise traceback because it gives the function name, div_zero. Syntax As you saw in the previous sections, a lambda form presents syntactic distinctions from a normal function. In particular, a lambda function has the following characteristics: It can only contain expressions and can’t include statements in its body. It is written as a single line of execution. It does not support type annotations. It can be immediately invoked (IIFE). No Statements A lambda function can’t contain any statements. In a lambda function, statements like return, pass, assert, or raise will raise a SyntaxError exception. Here’s an example of adding assert to the body of a lambda: >>> (lambda x: assert x == 2)(2) File "", line 1 (lambda x: assert x == 2)(2) ^ SyntaxError: invalid syntax This contrived example intended to assert that parameter x had a value of 2. But, the interpreter identifies a SyntaxError while parsing the code that involves the statement assert in the body of the lambda. Single Expression In contrast to a normal function, a Python lambda function is a single expression. Although, in the body of a lambda, you can spread the expression over several lines using parentheses or a multiline string, it remains a single expression: >>> (lambda x: ... (x % 2 and ''odd'' or ''even''))(3) ''odd'' The example above returns the string ''odd'' when the lambda argument is odd, and ''even'' when the argument is even. It spreads across two lines because it is contained in a set of parentheses, but it remains a single expression. Type Annotations If you’ve started adopting type hinting, which is now available in Python, then you have another good reason to prefer normal functions over Python lambda functions. Check out Python Type Checking (Guide) to get learn more about Python type hints and type checking. In a lambda function, there is no equivalent for the following:','2021-01-15 17:55:44.516760',1,1,NULL,NULL),
 (5,'outro texto python4','Explicando python','# **History** Alonzo Church formalized lambda calculus, a language based on pure abstraction, in the 1930s. Lambda functions are also referred to as lambda abstractions, a direct reference to the abstraction model of Alonzo Church’s original creation. Lambda calculus can encode any computation. It is Turing complete, but contrary to the concept of a Turing machine, it is pure and does not keep any state. Functional languages get their origin in mathematical logic and lambda calculus, while imperative programming languages embrace the state-based model of computation invented by Alan Turing. The two models of computation, lambda calculus and Turing machines, can be translated into each another. This equivalence is known as the Church-Turing hypothesis. Functional languages directly inherit the lambda calculus philosophy, adopting a declarative approach of programming that emphasizes abstraction, data transformation, composition, and purity (no state and no side effects). Examples of functional languages include Haskell, Lisp, or Erlang. By contrast, the Turing Machine led to imperative programming found in languages like Fortran, C, or Python. The imperative style consists of programming with statements, driving the flow of the program step by step with detailed instructions. This approach promotes mutation and requires managing state. The separation in both families presents some nuances, as some functional languages incorporate imperative features, like OCaml, while functional features have been permeating the imperative family of languages in particular with the introduction of lambda functions in Java, or Python. Python is not inherently a functional language, but it adopted some functional concepts early on. In January 1994, map(), filter(), reduce(), and the lambda operator were added to the language. First Example Here are a few examples to give you an appetite for some Python code, functional style. The identity function, a function that returns its argument, is expressed with a standard Python function definition using the keyword def as follows: >>> def identity(x): ... return x identity() takes an argument x and returns it upon invocation. In contrast, if you use a Python lambda construction, you get the following: >>> lambda x: x In the example above, the expression is composed of: The keyword: lambda A bound variable: x A body: x Note: In the context of this article, a bound variable is an argument to a lambda function. In contrast, a free variable is not bound and may be referenced in the body of the expression. A free variable can be a constant or a variable defined in the enclosing scope of the function. You can write a slightly more elaborated example, a function that adds 1 to an argument, as follows: >>> lambda x: x + 1 You can apply the function above to an argument by surrounding the function and its argument with parentheses: >>> (lambda x: x + 1)(2) 3 Reduction is a lambda calculus strategy to compute the value of the expression. In the current example, it consists of replacing the bound variable x with the argument 2: (lambda x: x + 1)(2) = lambda 2: 2 + 1 = 2 + 1 = 3 Because a lambda function is an expression, it can be named. Therefore you could write the previous code as follows: >>> add_one = lambda x: x + 1 >>> add_one(2) 3 The above lambda function is equivalent to writing this: def add_one(x): return x + 1 These functions all take a single argument. You may have noticed that, in the definition of the lambdas, the arguments don’t have parentheses around them. Multi-argument functions (functions that take more than one argument) are expressed in Python lambdas by listing arguments and separating them with a comma (,) but without surrounding them with parentheses: >>> full_name = lambda first, last: f''Full name: {first.title()} {last.title()}'' >>> full_name(''guido'', ''van rossum'') ''Full name: Guido Van Rossum'' The lambda function assigned to full_name takes two arguments and returns a string interpolating the two parameters first and last. As expected, the definition of the lambda lists the arguments with no parentheses, whereas calling the function is done exactly like a normal Python function, with parentheses surrounding the arguments. Remove ads Anonymous Functions The following terms may be used interchangeably depending on the programming language type and culture: Anonymous functions Lambda functions Lambda expressions Lambda abstractions Lambda form Function literals For the rest of this article after this section, you’ll mostly see the term lambda function. Taken literally, an anonymous function is a function without a name. In Python, an anonymous function is created with the lambda keyword. More loosely, it may or not be assigned a name. Consider a two-argument anonymous function defined with lambda but not bound to a variable. The lambda is not given a name: >>> lambda x, y: x + y The function above defines a lambda expression that takes two arguments and returns their sum. Other than providing you with the feedback that Python is perfectly fine with this form, it doesn’t lead to any practical use. You could invoke the function in the Python interpreter: >>> _(1, 2) 3 The example above is taking advantage of the interactive interpreter-only feature provided via the underscore (_). See the note below for more details. You could not write similar code in a Python module. Consider the _ in the interpreter as a side effect that you took advantage of. In a Python module, you would assign a name to the lambda, or you would pass the lambda to a function. You’ll use those two approaches later in this article. Note: In the interactive interpreter, the single underscore (_) is bound to the last expression evaluated. In the example above, the _ points to the lambda function. For more details about the usage of this special character in Python, check out The Meaning of Underscores in Python. Another pattern used in other languages like JavaScript is to immediately execute a Python lambda function. This is known as an Immediately Invoked Function Expression (IIFE, pronounce “iffy”). Here’s an example: >>> (lambda x, y: x + y)(2, 3) 5 The lambda function above is defined and then immediately called with two arguments (2 and 3). It returns the value 5, which is the sum of the arguments. Several examples in this tutorial use this format to highlight the anonymous aspect of a lambda function and avoid focusing on lambda in Python as a shorter way of defining a function. Python does not encourage using immediately invoked lambda expressions. It simply results from a lambda expression being callable, unlike the body of a normal function. Lambda functions are frequently used with higher-order functions, which take one or more functions as arguments or return one or more functions. A lambda function can be a higher-order function by taking a function (normal or lambda) as an argument like in the following contrived example: >>> high_ord_func = lambda x, func: x + func(x) >>> high_ord_func(2, lambda x: x * x) 6 >>> high_ord_func(2, lambda x: x + 3) 7 Python exposes higher-order functions as built-in functions or in the standard library. Examples include map(), filter(), functools.reduce(), as well as key functions like sort(), sorted(), min(), and max(). You’ll use lambda functions together with Python higher-order functions in Appropriate Uses of Lambda Expressions. Remove ads Python Lambda and Regular Functions This quote from the Python Design and History FAQ seems to set the tone about the overall expectation regarding the usage of lambda functions in Python: Unlike lambda forms in other languages, where they add functionality, Python lambdas are only a shorthand notation if you’re too lazy to define a function. (Source) Nevertheless, don’t let this statement deter you from using Python’s lambda. At first glance, you may accept that a lambda function is a function with some syntactic sugar shortening the code to define or invoke a function. The following sections highlight the commonalities and subtle differences between normal Python functions and lambda functions. Functions At this point, you may wonder what fundamentally distinguishes a lambda function bound to a variable from a regular function with a single return line: under the surface, almost nothing. Let’s verify how Python sees a function built with a single return statement versus a function constructed as an expression (lambda). The dis module exposes functions to analyze Python bytecode generated by the Python compiler: ```python import dis add = lambda x, y: x + y type(add) dis.dis(add) 1 0 LOAD_FAST 0 (x) 2 LOAD_FAST 1 (y) 4 BINARY_ADD 6 RETURN_VALUE add at 0x7f30c6ce9ea0> ``` You can see that dis() expose a readable version of the Python bytecode allowing the inspection of the low-level instructions that the Python interpreter will use while executing the program. Now see it with a regular function object: >>> import dis >>> def add(x, y): return x + y >>> type(add) >>> dis.dis(add) 1 0 LOAD_FAST 0 (x) 2 LOAD_FAST 1 (y) 4 BINARY_ADD 6 RETURN_VALUE >>> add The bytecode interpreted by Python is the same for both functions. But you may notice that the naming is different: the function name is add for a function defined with def, whereas the Python lambda function is seen as lambda. Traceback You saw in the previous section that, in the context of the lambda function, Python did not provide the name of the function, but only . This can be a limitation to consider when an exception occurs, and a traceback shows only : >>> div_zero = lambda x: x / 0 >>> div_zero(2) Traceback (most recent call last): File "", line 1, in File "", line 1, in ZeroDivisionError: division by zero The traceback of an exception raised while a lambda function is executed only identifies the function causing the exception as . Here’s the same exception raised by a normal function: >>> def div_zero(x): return x / 0 >>> div_zero(2) Traceback (most recent call last): File "", line 1, in File "", line 1, in div_zero ZeroDivisionError: division by zero The normal function causes a similar error but results in a more precise traceback because it gives the function name, div_zero. Syntax As you saw in the previous sections, a lambda form presents syntactic distinctions from a normal function. In particular, a lambda function has the following characteristics: It can only contain expressions and can’t include statements in its body. It is written as a single line of execution. It does not support type annotations. It can be immediately invoked (IIFE). No Statements A lambda function can’t contain any statements. In a lambda function, statements like return, pass, assert, or raise will raise a SyntaxError exception. Here’s an example of adding assert to the body of a lambda: >>> (lambda x: assert x == 2)(2) File "", line 1 (lambda x: assert x == 2)(2) ^ SyntaxError: invalid syntax This contrived example intended to assert that parameter x had a value of 2. But, the interpreter identifies a SyntaxError while parsing the code that involves the statement assert in the body of the lambda. Single Expression In contrast to a normal function, a Python lambda function is a single expression. Although, in the body of a lambda, you can spread the expression over several lines using parentheses or a multiline string, it remains a single expression: >>> (lambda x: ... (x % 2 and ''odd'' or ''even''))(3) ''odd'' The example above returns the string ''odd'' when the lambda argument is odd, and ''even'' when the argument is even. It spreads across two lines because it is contained in a set of parentheses, but it remains a single expression. Type Annotations If you’ve started adopting type hinting, which is now available in Python, then you have another good reason to prefer normal functions over Python lambda functions. Check out Python Type Checking (Guide) to get learn more about Python type hints and type checking. In a lambda function, there is no equivalent for the following:','2021-01-15 18:03:36.479884',2,2,NULL,NULL),
 (6,'outro texto python5','outro teste dse python','# **History**
adsa
> Alonzo Church formalized lambda calculus, a language based on pure abstraction, in the 1930s. Lambda functions are also referred to as lambda abstractions, a direct reference to the abstraction model of Alonzo Church’s original creation.

> Alonzo Church formalized lambda calculus, a language based on pure abstraction, in the 1930s. Lambda functions are also referred to as lambda abstractions, a direct reference to the abstraction model of Alonzo Church’s original creation.

*lambda calculus can encode any computation. it is turing complete, but contrary to the concept of a turing machine, it is pure and does not keep any state.lambda calculus can encode any computation. it is turing complete, but contrary to the concept of a turing machine, it is pure and does not keep any state.*

Functional languages get their origin in mathematical logic and lambda calculus, while imperative programming languages embrace the state-based model of computation invented by Alan Turing. The two models of computation, lambda calculus and Turing machines, can be translated into each another. This equivalence is known as the Church-Turing hypothesis.

` teste `

| Teste | teste2  |
| :------------ | :------------ |
| sobre algo  |  falando |
| continua  | mais um pouco  |



![teste](https://miro.medium.com/max/1000/0*8b65gImRyURzzMFi "teste")

[Wiki](http://127.0.0.1:5000/wiki/index "Wiki")

###### teste','2021-01-15 18:30:47.182852',1,1,'2021-01-20 03:38:12.947788',1);
DROP TABLE IF EXISTS `alembic_version`;
CREATE TABLE IF NOT EXISTS `alembic_version` (
	`version_num`	VARCHAR ( 32 ) NOT NULL,
	CONSTRAINT `alembic_version_pkc` PRIMARY KEY(`version_num`)
);
INSERT INTO `alembic_version` (version_num) VALUES ('536ab7071e76');
DROP INDEX IF EXISTS `ix_user_username`;
CREATE UNIQUE INDEX IF NOT EXISTS `ix_user_username` ON `user` (
	`username`
);
DROP INDEX IF EXISTS `ix_user_name`;
CREATE INDEX IF NOT EXISTS `ix_user_name` ON `user` (
	`name`
);
DROP INDEX IF EXISTS `ix_user_email`;
CREATE UNIQUE INDEX IF NOT EXISTS `ix_user_email` ON `user` (
	`email`
);
DROP INDEX IF EXISTS `ix_topic_timestamp`;
CREATE INDEX IF NOT EXISTS `ix_topic_timestamp` ON `topic` (
	`timestamp`
);
DROP INDEX IF EXISTS `ix_topic_formated_name`;
CREATE UNIQUE INDEX IF NOT EXISTS `ix_topic_formated_name` ON `topic` (
	`formated_name`
);
DROP INDEX IF EXISTS `ix_topic__name`;
CREATE UNIQUE INDEX IF NOT EXISTS `ix_topic__name` ON `topic` (
	`_name`
);
DROP INDEX IF EXISTS `ix_tag_timestamp`;
CREATE INDEX IF NOT EXISTS `ix_tag_timestamp` ON `tag` (
	`timestamp`
);
DROP INDEX IF EXISTS `ix_tag_name`;
CREATE INDEX IF NOT EXISTS `ix_tag_name` ON `tag` (
	`name`
);
DROP INDEX IF EXISTS `ix_article_view_last_view`;
CREATE INDEX IF NOT EXISTS `ix_article_view_last_view` ON `article_view` (
	`last_view`
);
DROP INDEX IF EXISTS `ix_article_view_first_view`;
CREATE INDEX IF NOT EXISTS `ix_article_view_first_view` ON `article_view` (
	`first_view`
);
DROP INDEX IF EXISTS `ix_article_updated_timestamp`;
CREATE INDEX IF NOT EXISTS `ix_article_updated_timestamp` ON `article` (
	`updated_timestamp`
);
DROP INDEX IF EXISTS `ix_article_title`;
CREATE UNIQUE INDEX IF NOT EXISTS `ix_article_title` ON `article` (
	`title`
);
DROP INDEX IF EXISTS `ix_article_timestamp`;
CREATE INDEX IF NOT EXISTS `ix_article_timestamp` ON `article` (
	`timestamp`
);
COMMIT;
