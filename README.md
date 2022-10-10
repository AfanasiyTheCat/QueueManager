

# Эмулятор системы массового обслуживания.


Имеется _n_ касс.

Через каждый случайный период времени в секундах (выбирается на отрезке [1,_t_]) приходит случайное число людей (выбирается на отрезке [0,_p_])),
каждый из которых становится в минимальную очередь на одну из касс.

Каждая касса обслуживает человека случайный период времени в
секундах.

Требуется реализовать вышеописанный эмулятор с возможностью устанавливать значения _n_, _t_, _p_  и всех _C_, в режиме реального времени.

Программа должна обладать удобной графической оболочкой, предоставляющей все необходимые элементы управления для задания
параметров и дающей полное представление о текущем состоянии касс (в том числе, среднее время обслуживания за все время работы, длина очереди). Также требуется
реализовать валидацию ввода, подсвечивать самую загруженную и свободную кассы, обеспечить возможность приостановки/запуска всего процесса.
