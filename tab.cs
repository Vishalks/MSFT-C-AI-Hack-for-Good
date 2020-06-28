using System;

namespace ChannelGroupTab
{
    public class Tab
    {
        public string Message { get; set; }

        public string GetColor()
        {
            Message = "Tab.cs says: 'Hi, You chose";
            return Message;
        }
    }
}

