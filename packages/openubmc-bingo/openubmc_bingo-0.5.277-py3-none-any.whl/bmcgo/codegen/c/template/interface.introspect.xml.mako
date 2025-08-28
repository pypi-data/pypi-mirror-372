<!DOCTYPE node PUBLIC
"-//freedesktop//DTD D-BUS Object Introspection 1.0//EN"
"http://www.freedesktop.org/standards/dbus/1.0/introspect.dtd"
>
<node>
% for intf in interfaces:
    % for text in intf.comment.texts:
  <!-- ${text} -->
    % endfor
  <interface name="${intf.name}">
    ### 接口注释
    % for anno in intf.annotations:
    <annotation name="${anno.name}" value="${anno.value}"/>
    % endfor
    ### 属性
    % for prop in intf.properties:
        % if not prop.private:
        % for text in prop.comment.texts:
    <!-- ${text} -->
        % endfor
        % if len(prop.annotations) > 0:
    <property name="${prop.name}" type="${prop.signature}" access="${prop.access}">
            % for anno in prop.annotations:
                % for text in anno.comment.texts:
      <!-- ${text} -->
                % endfor
      <annotation name="${anno.name}" value="${anno.value}"/>
            % endfor
    </property>
        % else:
    <property name="${prop.name}" type="${prop.signature}" access="${prop.access}"/>
        % endif
        % endif
    % endfor
    ### 方法
    % for method in intf.methods:
        % for text in method.comment.texts:
    <!-- ${text} -->
        % endfor
    <method name="${method.name}">
        % for anno in method.annotations:
            % for text in anno.comment.texts:
      <!-- ${text} -->
            % endfor
      <annotation name="${anno.name}" value="${anno.value}"/>
        % endfor
        % for arg in method.req_args:
            % for text in arg.comment.texts:
      <!-- ${text} -->
            % endfor
            % if len(arg.name) > 0:
      <arg name="${arg.name}" direction="${arg.direction}" type="${arg.signature}"/>
            % else:
      <arg direction="${arg.direction}" type="${arg.signature}"/>
            % endif
        % endfor
        % for arg in method.rsp_args:
            % for text in arg.comment.texts:
      <!-- ${text} -->
            % endfor
            % if len(arg.name) > 0:
      <arg name="${arg.name}" direction="${arg.direction}" type="${arg.signature}"/>
            % else:
      <arg direction="${arg.direction}" type="${arg.signature}"/>
            % endif
        % endfor
    </method>
    % endfor
    ### 方法
    % for signal in intf.signals:
        % for text in signal.comment.texts:
    <!-- ${text} -->
        % endfor
        %if len(signal.annotations) > 0 or len(signal.args) > 0:
    <signal name="${signal.name}">
            % for anno in signal.annotations:
                % for text in anno.comment.texts:
      <!-- ${text} -->
                % endfor
      <annotation name="${anno.name}" value="${anno.value}"/>
            % endfor
            % for arg in signal.args:
                % for text in arg.comment.texts:
      <!-- ${text} -->
                % endfor
                % if len(arg.name) > 0:
      <arg name="${arg.name}" type="${arg.signature}"/>
                % else:
      <arg type="${arg.signature}"/>
                % endif
            % endfor
    </signal>
        % else:
    <signal name="${signal.name}"/>
        % endif
    % endfor
  </interface>
% endfor
</node>